+++
title = "Passing strings between TinyGo and JavaScript"
author = ["Alex Carney"]
description = "Figuring out how WebAssembly handles memory"
date = 2020-04-30
draft = false
tags = ["go", "tinygo", "wasm", "js"]
+++

After getting a ["Hello, World!"]({{< ref "hello-world-tinygo-wasm.md" >}}) WebAssembly
application working I thought it would be fun to try and implement a toy programming
language in the browser. However before I could even start thinking about parsers,
abstract syntax trees and the like I had to be able to pass strings between my
WebAssembly module and the surrounding JavaScript.

Turns out that is much trickier than I expected.


<!--more-->

> **Disclaimer:**
>
> I definitely don't know what I'm doing, if there's a better way of doing this I'd love
> to know about it! 🙂

## The Interface

{{< figure src="/images/wasm-input-output.png" caption="The Interface to our 'interpreter'" link="/images/wasm-input-output.png">}}

Our WebAssembly module needs a way to interact with the user in order both collect input
and show the output. So to start with I updated the webpage from the previous post to
include a number of `textarea` elements and a "Run" button.

```html
<div>
    <h3>Input</h3>
    <textarea id="input"></textarea>
</div>
<div>
    <button disabled id="run-button">Run</button>
</div>
<div>
    <h3>Output</h3>
    <textarea disabled id="output"></textarea>
</div>
<div class="log-area">
    <textarea disabled id="log"></textarea>
</div>
```

Now we could just use the `println` function to do the equivalent of a `console.log`
from our TinyGo code but it could be useful to have a log on screen to provide feedback
to the user.

## Passing strings from TinyGo to JavaScript

To achieve this we first need a JavaScript function which takes some text and appends it
to the "log" `textarea` element on screen.

```js
const log = document.getElementById('log')

function logText(text) {
    log.value += text + '\n'
}
```

Next we need some way to reference such a function from our go code. If we define a
function but not implement it TinyGo will recognise it as an external function whose
implementation should be provided by the surrounding JavaScript.

```go
package main

func log(message string)

func main() {
    log("Hello, World!")
}
```

> **Note:**
>
> The Go tools inside of VSCode will complain about the missing implementation for the
> `log` function but TinyGo itself will compile this happily.

Lastly all we have to do is adjust our wrapping JavaScript code to pass in the
implementation for the `log` function to the module's envrionment. While we're at we
might as well wire up that "Run" button.

```js
...

function onRun(runner, wasm) {
    return (event) => runner.run(wasm)
}

go.importObject["main.go.log"] = logText

WebAssembly.instantiateStreaming(fetch("/js/wisp.wasm"), go.importObject)
    .then(module => {
        let wasm = module.instance

        runButton.disabled = false
        runButton.addEventListener('click', onRun(go, wasm))
    })
```

That should be everything connected up, time to give it a whirl!

{{< figure src="/images/wasm-addr.png" caption="Not exactly what I had in mind..." link="/images/wasm-addr.png" >}}

Hmm... 🤔

This result quickly prompted an exetended session of searching around for the "right"
way to pass values back and forth between my WebAssembly module and the surrounding
JavaScript code. Unfortunately I didn't really come across anything that seemed to work
for me.

I did find that Go has a [syscall/js][go-syscall-js] module which seems to handle
exactly this kind of thing along with a [tutorial series][go-wasm-tutorial] that makes
use of it. The problem is that it seems to fly in the face of the
[examples][tinygo-wasm-example] (which I did manage to reproduce) on the TinyGo
website where it appears the compiler is handling most of these details.

Unable to find an example to copy I decided it was time for a peek behind the curtain...

### Digging Deeper

On my travels I did manage to find out some more information about WebAssembly itself

- WebAssembly only has basic integer and float [types][wasm-types]
- A module has its own [memory][wasm-memory] and is represented by an `ArrayBuffer` in
  JavaScript code.

Before long I had a hunch that the random number that was being displayed in the
`textarea` element was in fact the memory address of the string to be logged. If that
was the case, how should the memory in that location be interpreted so that we're
able to extract a string from it?

After some more research I discovered that TinyGo is using the [LLVM][llvm] compiler
toolchain and that you can ask it for the [itermediate representation][llvm-ir] which it
passes to LLVM in order to generate the WebAssembly code.

```sh
$ tinygo build -no-debug -target wasm -printir -o public/js/wisp.wasm main.go > debug.txt
```

Now, there is a *lot* going on (20,000+ lines) in this file as it includes not just our
simple program but the Go runtime required to execute it. Thankfully with `Ctrl-F` to
the rescue, it's easy enough to track down where our "Hello, World!" string is defined

```llvm
...
@"main.go.main$string" = internal unnamed_addr constant [13 x i8] c"Hello, World!"
...
```

I don't know the first thing when it comes to LLVM's IR representation of code but after
looking into how it thinks about [arrays][llvm-array] we see that `[13 x i8]` indicates
that our string is represented by an array of 13, 8-byte integers.

Awesome, we now know how to interpret the values we see in the WebAssembly module's
`ArrayBuffer`, but how will we know how many values to look for?

Let's try and find our `log` function...

```llvm
declare void @main.go.log(i8*, i32, i8*, i8*)
```

Ah, just like the `log` function in our go code it has no implementation since this is
to be provided by the JavaScript wrapper. However instead of a single argument it now
takes 4! Interesting... let's track down our main function and see how it is used.

```llvm
define dso_local void @main.go.main(i8* %context, i8* %parentHandle) unnamed_addr {
entry:
  call void @main.go.log(i8* getelementptr inbounds ([13 x i8], [13 x i8]* @"main.go.main$string", i32 0, i32 0), i32 13, i8* undef, i8* undef)
  ret void
}
```

Wow. Umm, there's a lot going on here... what if we try "squinting" at this code a bit

```llvm
define void @main.go.main(...) {
  call @main.go.log(i8* getelementptr (... @"main.go.main$string",...), i32 13, ...)
  ret void
}
```

Ok, so it looks like there's a call being made to our log function and
[getelementptr][llvm-getelementptr] appears to be returning the memory address of our
"Hello, World!" string and look! The `i32 13` argument appears to be passing in its
length! I have no idea what the other arguments are supposed to represent so let's just
ignore those for now! 😃

Instead why don't we tweak our `logText` implementation of this function to take a
second argument and see what happens

```js
function logText(addr, length) {
    log.value += addr + " " + length + '\n'
}
```

{{< figure src="/images/wasm-addr-length.png" caption="That looks promising!" link="/images/wasm-addr-length.png" >}}

### Extracting the String

Assuming our assumptions are correct we should now have all the information we need in
order to extract the string from the WebAssembly module's memory. `ArrayBuffer` objects
in JavaScript don't seem to be the most intuitive to work with but I was eventually able
to come up with this.

```js
function logText(addr, length) {
    let memory = wasm.exports.memory
    let bytes = memory.buffer.slice(addr, addr + length)
    let text = String.fromCharCode.apply(null, new Int8Array(bytes))

    log.value += text + '\n'
}
```

After getting the reference to the `memory` object we use the [slice][array-buffer-slice]
method to obtain a copy of only the bytes that represent our string. Unfortunately bytes
on their own are meaningless unless you know how to interpret them. To enable this there
is a whole collection of [views][array-buffer-views] that can be wrapped around a given
array of bytes to attach meaning to them. From our explorations above we know that we
should use an `Int8Array`.

From there we map the `String.fromCharCode` function over the array of ints to convert
them to a string. Finally, we should be able to see our "Hello, World!" string output to
the log area

{{< figure src="/images/wasm-log-hello.png" caption="Success!" link="/images/wasm-log-hello.png" >}}

This did require a slight tweak to the way we load the module so that we have a global
`wasm` reference that our `logText` function is able to use to access the module
instance directly.

```js
let wasm

...

WebAssembly.instantiateStreaming(fetch("/js/wisp.wasm"), go.importObject)
    .then(module => {
        wasm = module.instance

        runButton.disabled = false
        runButton.addEventListener('click', onRun(go, wasm))
    })
```

## Passing strings from JavaScript to TinyGo

Phew, at least we're halfway there! Now that we've figured out how things actually hang
together it's "just" a matter of doing the inverse process to pass a string from our
JavaScript code into our WebAssembly module. As a proof of concept let's create an
`echo` function in TinyGo that will simply log whatever text it recieves.

```go
//go:export echo
func echo(message string) {
    log(message)
}
```

In order to actually pass a string to this function, we need to insert the string into
the memory of the WebAssembly module before calling `echo` with its address and length.

### Manipulating Memory

The problem is, where exactly in the module's memory should we place the string? We
can't shove it anywhere as we could corrupt memory required for some other part of the
program. It is possible to [grow][wasm-grow] the memory assigned to a module instance
which technically would be free for us to use(?) But it doesn't exactly *feel* right,
having two competing codebases manipulate the same memory layout seems to be asking
for trouble...

Thankfully I came across [this comment][tinygo-issue] on an issue in the TinyGo project
which provides a way we can work around this.

```go
var buf [1024]byte

//go:export getBuffer
func getBuffer() *byte {
    return &buf[0]
}
```

If we declare an array of bytes in the module, the TinyGo compiler will allocate space
and manage it for us. Then by exporting the `getBuffer` function we provide a way for
our wrapping JavaScript to ask for the address to the region of memory we have reserved
for it. This region of memory should then be safe for us to write to from JavaScript
**provided our go code only reads from this array**

Now with some reserved memory to use we can write a function that takes a string and
inserts it into the module's memory.

```js
function insertText(text, module) {

    // Get the address of the writable memory.
    let addr = module.exports.getBuffer()
    let buffer = module.exports.memory.buffer

    let mem = new Int8Array(buffer)
    let view = mem.subarray(addr, addr + text.length)

    for (let i = 0; i < text.length; i++) {
        view[i] = text.charCodeAt(i)
    }

    // Return the address we started at.
    return addr
}
```

As with the earlier case, we need to create an `Int8Array` in order to attach meaning to
the bytes and so that the numbers representing the characters in the string are encoded
correctly. Also note that we're using the [subarray][array-buffer-subarray] method this
time so that we're modifying the original array and not a copy.

### Calling the Echo Function

With a way for us to insert the string we want into the module's memory we should now
be in a position to call the `echo` function passing the starting address and length
of the string we want it to echo. However instead of hardcoding the string this time why
don't we take it from the input `textarea` we have on the page.

```js
const input = document.getElementById('input')

function onRun(runner, module) {
    return (event) => {
        // First, we need to run the module in order to define everything.
        runner.run(module)

        let inputText = input.value
        let addr = insertText(inputText, module)

        // Now just pass the memory location to the relevant function.
        module.exports.echo(addr, inputText.length)
    }
}
```

{{< figure src="/images/wasm-echo.gif" caption="" link="/images/wasm-echo.gif" >}}

## Wrapping Up

We made it! That was certainly a lot more involved than I expected it to be, but if
nothing else it's forced me to learn a bit more about some of the lower-level details
of working with WebAssembly modules.

I don't think this is necessarily the right approach though.. ok we're able to pass a
(simple!) string back and forth between our TinyGo code and JavaScript. But there are
more details that still need to be considered

- This solution does not handle Unicode - in fact while writing this post I discovered
  that it doesn't even handle every ASCII character! There is however a
  [TextEncoder][js-text-encoder] API available in the browser that looks like it might
  go some way towards fixing this.

- I thought the fixed buffer size in the go module would be an issue - how would you
  handle inputs larger than 1024 bytes? However after a quick test with about 5K of text
  it seemed to not matter? 🤷 Though I'm sure there's ways to break it.

- Finally, what about more complex data structures? Sure we'd probably be able to encode
  them as JSON and pass them around that way but I'm sure that would introduce
  unnecessary overhead.

And with all that said isn't this a problem that the toolchain should be solving? 🤔


[array-buffer-slice]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/ArrayBuffer/slice
[array-buffer-subarray]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray/subarray
[array-buffer-views]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/TypedArray
[go-syscall-js]: https://golang.org/pkg/syscall/js/
[go-wasm-tutorial]: https://www.aaron-powell.com/posts/2019-02-06-golang-wasm-3-interacting-with-js-from-go/
[js-text-encoder]: https://developer.mozilla.org/en-US/docs/Web/API/TextEncoder
[llvm]: https://llvm.org/
[llvm-array]: https://llvm.org/docs/LangRef.html#array-type
[llvm-getelementptr]: https://llvm.org/docs/LangRef.html#i-getelementptr
[llvm-ir]: https://llvm.org/docs/LangRef.html#abstract
[tinygo-issue]: https://github.com/tinygo-org/tinygo/issues/411#issuecomment-503066868
[tinygo-wasm-example]: https://tinygo.org/webassembly/webassembly/
[wasm-grow]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/Memory/grow
[wasm-memory]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/Memory
[wasm-types]: https://webassembly.github.io/spec/core/syntax/types.html