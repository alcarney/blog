+++
title = "Deserialising Abstract Classes with Jackson"
description = "Parsing JSON into different class instances based on the value of a given field."
tags = ["java", "json"]
+++

Jackson can automatically detect the relevant abstract class to initialise when
parsing some JSON if you give it a little bit of help. There are multiple
methods Jackson can use to detect and indicate the class it should use but the
method I have chosen is to tell it to look for a `type` field.

Consider the following json snippets

{{< highlight nil >}}
{
    "id": "123",
    "type": "name",
    "name": "Alex"
}
{{< /highlight >}}

{{< highlight nil >}}
{
    "id": "345",
    "type": "value",
    "value": 123.4
}
{{< /highlight >}}

Which can be represented by the following classes

{{< highlight java >}}
public class IdName extends IdField {
    public static final String FIELD_TYPE = "name";
    private String name;

    public IdName() {
        super(FIELD_TYPE);
    }

    ...
}
{{< /highlight >}}

{{< highlight java >}}
public class IdValue extends IdField {
    public static final String FIELD_TYPE = "value";
    private float value;

    public IdValue() {
        super(FIELD_TYPE);
    }

    ...
}
{{< /highlight >}}

Then to enable Jackson to determine which subclass to initialise we need to add
some annotations to the base class definition

{{< highlight java >}}
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.EXISTING_PROPERTY, property = "type")
@JsonSubTypes({
        @JsonSubTypes.Type(value = IdName.class, name = IdName.FIELD_TYPE),
            @JsonSubTypes.Type(value = IdValue.class, name = IdValue.FIELD_TYPE)
})
public abstract class IdField {
    private String id;
    private String type;

    public IdField(String type) {
        this.id = UUID.randomUUID().toString();
        this.type = type;
    }

    ...
}
{{< /highlight >}}

Then we can just parse the json as we normally would.

{{< highlight java >}}
String jsonStr = "{\"id\":\"123\",\"name\":\"Alex\"}";
ObjectMapper mapper = new ObjectMapper();

IdField field = mapper.readValue(jsonStr, IdField.class);
System.out.println(field.getType());                        // => "name"

IdName nameField = (IdName) field;
System.out.println(nameField.getName());                    // => "Alex"
{{< /highlight >}}