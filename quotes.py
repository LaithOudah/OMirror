import unirest

# These code snippets use an open-source library. http://unirest.io/python
response = unirest.post("https://andruxnet-random-famous-quotes.p.mashape.com/?cat=famous&count=10",
  headers={
    "X-Mashape-Key": "GXdpPKkvT2msh6o4cTOkReQ3k2pGp1apsMbjsnFxVchoSW3IMz",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
  }
)

print(response.body[0])