API Keys
========

This is the document you can use to reference which API keys originate from where, and where you'll be able to get an API key.  
API Keys listed are in alphabetical order.  

Whenever a module is created that requires an API key, please edit this document and `config.example.json` accordingly.  

Format:

```
### Name

This is the API Key for the `service` service  

Small description about service  

Name in config.json: `name`  
This API key is used in the following module(s): `module.py`  
Website: http://somesite.com  
Get your own API key here: http://somesite.com/api  
Registration Required: Yes/No  
Free: Yes/No  
API Limitations (if any): Restricted to 1.000 calls per month  
```

-----

### scenes.at

This is the API Key for the `scenes.at` service.

Scenes.at is a url shortening service.  
This tool can be found in `tools/shorturl.py`, an API key should be passed as parameter.  
  
Name in config.json: `scenesat`  
This API key is used in the following module: None.  
Website: http://scenes.at/  
Get your own API key here: http://scenes.at/contact  
Registration Required: Apply through contact form.  
Free: Yes  
API Limitations: Unknown.  

### Wolfram Alpha

This is the API Key for the `Wolfram|Alpha` service.  

Wolfram Alpha is a computational knowledge engine.  
  
Name in config.json: `wolframalpha`  
This API key is used in the following module: `wolfram_alpha.py`  
Website: http://wolframalpha.com  
Get your own API key here: http://products.wolframalpha.com/api/  
Registration Required: No  
Free: Yes  
API Limitations: Restricted to 2.000 non-commercial API calls per month  

