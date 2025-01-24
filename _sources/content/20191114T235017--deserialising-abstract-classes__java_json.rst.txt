Deserialising Abstract Classes with Jackson
===========================================

Jackson can automatically detect the relevant abstract class to initialise when
parsing some JSON if you give it a little bit of help. There are multiple
methods Jackson can use to detect and indicate the class it should use but the
method I have chosen is to tell it to look for a ``type`` field.

Consider the following json snippets

.. container:: flex flex-col lg:flex-row justify-around

   .. code-block:: json
      :class: w-full lg:w-1/2 lg:mr-2   

      {
         "id": "123",
         "type": "name",
         "name": "Alex"
      }

   .. code-block:: json 
      :class: w-full lg:w-1/2 lg:ml-2

      {
         "id": "345",
         "type": "value",
         "value": 123.4
      }

Which can be represented by the following classes

.. container:: flex flex-col lg:flex-row justify-around

   .. code-block:: java 
      :class: w-full lg:w-1/2 lg:mr-2
      
      public class IdName extends IdField {
         public static final String FIELD_TYPE = "name";
         private String name;

         public IdName() {
            super(FIELD_TYPE);
         }

         ...
      }

   .. code-block:: java
      :class: w-full lg:w-1/2 lg:ml-2

      public class IdValue extends IdField {
         public static final String FIELD_TYPE = "value"; 
         private float value;

         public IdValue() {
            super(FIELD_TYPE);
         }

         ...
      }

We can then add a few annotations to the base abstract class telling Jackson to 
check the value of the ``type`` field and have it pick the correct concrete class
automatically. 

.. code-block:: java

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

Then we can just parse the json as we normally would.

.. code-block:: java

   String jsonStr = "{\"id\":\"123\",\"name\":\"Alex\"}";
   ObjectMapper mapper = new ObjectMapper();

   IdField field = mapper.readValue(jsonStr, IdField.class);
   System.out.println(field.getType());                        // => "name"

   IdName nameField = (IdName) field;
   System.out.println(nameField.getName());                    // => "Alex"