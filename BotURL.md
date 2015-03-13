Introduce Google Wave robot: BotURL

# [BotURL](http://wave-samples-gallery.appspot.com/about_app?app_id=18012) #

BotURL can replace a FULL URL with a hyperlink automatically.


## Address ##
  * boturl@appspot.com


## Usage ##
  * Just add BotURL as a participant, it will take care of the rest by default.
  * You can also include these commands in your blip to use some additional features:
| **boturl:no** | BotURL will leave this blip alone |
|:--------------|:----------------------------------|
| **boturl:title** | (**NOT stable!**) BotURL will replace the URLs in this blip with page titles |
| **boturl:help** | Print help message |


## Notice ##
BotURL only responses to **FULL** URLs, that means it will only response to "**HTTP://**www.google.com" and will do nothing about "www.google.com"

**E.g.**:
| **Original text** | **Replacement** | **Shorten URL** | **[Anti-phishing](http://en.wikipedia.org/wiki/Phishing)** | **Expand URL** | **Title** |
|:------------------|:----------------|:----------------|:-----------------------------------------------------------|:---------------|:----------|
| http://www.google.com | [[google.com/...](http://www.google.com)] | YES |  |  |  |
| http://www.google.com@members.tripod.com | [[members.tripod.com/...](http://www.google.com@members.tripod.com)] | YES | YES |  |  |
| http://tinyurl/dehdc | [[google.com/...](http://www.google.com)] |  |  | YES |  |
| http://bit.ly/1RmnUT | [[google.com/...](http://www.google.com)] |  |  | YES |  |
| http://bit.ly/MgOyD **boturl:title** | [[百度一下，你就知道](http://www.baidu.com)] |  |  | YES | YES |
| http://www.baidu.com **boturl:title** | [[百度一下，你就知道](http://www.baidu.com)] |  |  |  | YES |