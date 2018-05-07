{
      "$schema": "http://json-schema.org/draft-07/schema#",
	  "title": "Montura",
	  "description": "Información de la montura",
	  "type": "object",
	  "properties": {
	          "azimut": {
		            "description": "El azimut",
		            "type": "number"
		          },
	          "altura": {
		            "description": "La altura",
		            "type": "number"
		          }
	        },"required": ["azimut","altura"]
}
