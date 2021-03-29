# HOW TO CREATE A NEW LAYER

1. Create a function which defines the view and add a comment for the API-function. For testing, create the function via DBeaver, execute the following query and check if the new function is listed: 
    ```
    SELECT jsonb_pretty(metadata) FROM layer_metadata 
    ```

2. Create a style and store it in app/client/public/static/layer-styles/styles. 

3. Add the translations for the layer legend in app/client/public/static/layer-styles/translations.

4. Adjust the "app-conf.json" file:

    - set type
        ``` 
        "type": "VECTORTILE" 
        ``` 
    - set format
        ``` 
        "format": "MVT" 
        ``` 
    
    - adjust URL, e.g.:
        ```
        "url": "/v2/map/study_area/{z}/{x}/{y}"
        ```

    - Connect layer with style by adding the following code: 
        ``` 
            "style": {
                "format": "geostyler",
                "url": "./static/layer-styles/styles/study_area.json"
                } 	
        ``` 