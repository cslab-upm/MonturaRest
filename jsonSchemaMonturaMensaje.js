{
      "$schema": "http://json-schema.org/draft-07/schema#",
	  "title": "MonturaMensaje",
	  "description": "Peticion a la montura",
	  "type": "object",
	  "properties": {
	          "comando": {
		            "description": "Comando que se quiere que ejecute la montura",
		            "type": "string",
		            "enum":["moverNorte","parar"]
		          },
	          "parametros": {
		            "description": "Parametros de la funcion",
		            "type": "array"
		          }
	        },"required": ["comando"]
}
