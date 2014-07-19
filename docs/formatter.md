tools/formatter.py
==================

Formatter.py is a tool that you can use to format colours and formatting into human readable strings.  

The parser will replace messages using a $(colour) or $(formatting) syntax, with $+ to concatinate strings together should you need colours in the middle of a sentence.  
You will not need to concatinate colours to strings if you're worried about double whitespaces; the parser takes care of that.  

For a full list of things you can format, call the methods `getAvailableColours()` and `getAvailableFormats()`,  


Below is a small script on how to use the formatter, since code speaks louder than words.

```
from tools import formatter


messages = [
    "Hey there $(red) {} $+ $(clear) , what's going on?".format("Zarthus"),
    "Hey there $(dblue) Zarthus $+ $(clear) , what's going on?",
    "This is a $(green) foreground $+ $(clear) , but also supports $(green,blue) backgrounds $+ $(clear) .",
    ("Should you (for whatever insane reason) wish to make an instanely long string of colours, we've got that " +
        "covered, $(green,orange,yellow,blue,white,black,dblue) you're pretty insane though. And PRs with this " +
            "kind of code will not be accepted"),
    ("Things to note is that colour codes do not support spaces between commas, and that you can mix" + 
        "formatting with colours. E.g. $(red,bold) mixing bold+red, or $(clear, blue, white) spaces"),
    ("As is, there is no way to escape formatting either, if your string requires you to use $( ) in a literal syntax" +
        ", you'll need to script around it. The syntax however, was designed so that it would not interfere with " +
            "normal strings"),
    "$(red,green) if you thought that was all, $(clear,green,bold) well you're probably right."
]

parser = formatter.IrcFormatter()

for message in messages:
    print(parser.parse(message))

```

Output:
```
Hey there 04Zarthus, what's going on? 
Hey there 02Zarthus, what's going on? 
This is a 09foreground, but also supports 09,12backgrounds. 
Should you (for whatever insane reason) wish to make an instanely long string of colours, we've got that covered, 09,0708,1200,0102you're pretty insane though. And PRs with this kind of code will not be accepted 
Things to note is that colour codes do not support spaces between commas, and that you can mixformatting with colours. E.g. 04mixing bold+red, or $(clear, blue, white) spaces 
As is, there is no way to escape formatting either, if your string requires you to use $( ) in a literal syntax, you'll need to script around it. The syntax however, was designed so that it would not interfere with normal strings 
04,09if you thought that was all, 09well you're probably right. 
```

Respectively, the `strip()` method removes this kind of formatting.