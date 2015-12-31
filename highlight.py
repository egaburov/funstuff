#!/usr/bin/env python
# $ python highlight.py source.cpp  [-o out.html]
# $ chrome open source.cpp.html
# This tool requires "highlight" tool: http://andre-simon.de/index.php

import sys
import subprocess
import urllib2
import os
from math import log10,ceil

header_template="""
<html>
<head>
<style type=text/css> 
a:link {
    background-color: #f8f8f8
}
  
a:hover {
    background-color: #eef;
    display:block
}
span:target, span.sftarget { 
  background-color: #f6ebbb;
  margin-right:-8px;
} 
div.CodeBox {
  padding:2px;
  margin-bottom:18px;
}
code.CodeBody {
  float: left;
  margin: 0;
  border: solid 1px #ddd;
  margin-left:-1px;
  padding-right:8px;
}
code.LineNumbers {
  float: left;
  margin: 0;
  padding-right:0px;
  border: solid 1px #ddd;
  margin-right:00px;
  background: #F6F6F6
}
span.linenumber {
  height:15px;
  white-space: pre;
  display: block;
  width: %dpx;
}
span.codeline {
  padding-left:5px;
  display: block;
  height:15px;
  white-space: pre;
}
a.falseLinks{
  text-align:right;
 }
</style>
%s
<script type="text/javascript"><!--//--><![CDATA[//><!--

sfTarget = function() {
  var sfEls=document.getElementsByTagName("A");
  var aEls = document.getElementsByTagName("A");
  document.lastTarget = null;
  for (var i=0; i<sfEls.length; i++) {
    if (sfEls[i].name) {
      if (location.hash==("#" + sfEls[i].name)) {
        sfEls[i].className+=" " + cls;
        document.lastTarget=sfEls[i];
      }
      for (var j=0; j<aEls.length; j++) {
        if (aEls[j].hash==("#" + sfEls[i].name)) aEls[j].targetEl = sfEls[i]; aEls[j].onclick = function() {
          if (document.lastTarget) document.lastTarget.className = document.lastTarget.className.replace(new RegExp(" sftarget\\b"), "");
          if (this.targetEl) this.targetEl.className+=" sftarget"; document.lastTarget=this.targetEl;
          return true;
        }
      }
    }
  }
}
if (window.attachEvent) window.attachEvent("onload", sfTarget);

// alternative way to handle anchor (jerky on Chrome/FF)
function keepLocation(oldOffset) {
  if (window.pageYOffset!= null){
    st=oldOffset;
  }
  if (document.body.scrollWidth!= null){
    st=oldOffset;
  }
  setTimeout('window.scrollTo(0,st)',0);
}
// handle onload 
function scrollDown() {
  var url = document.location.href;
  if (url.indexOf('#') != -1)
  {
    st = $(window.location.hash).offset().top-window.innerHeight/3;
    setTimeout('window.scrollTo(0,st)',0);
  }
}
// handle anchors
$(function() {
  $("a.falseLinks").click(function(e) {
    // ...other stuff you want to do when links is clicked
    e.preventDefault();
    var offset = window.pageYOffset;
    window.location=this.href;
    $('html,body').scrollTop(offset);
    // This is the same as putting onclick="return false;" in HTML
   return false;
  })
});
//--><!]]></script>
</head>
<body style=background-color:#ffffff onload="scrollDown()">
<tt>
<div class="CodeBox">
"""

jquery="""
<script src="http://ajax.aspnetcdn.com/ajax/jQuery/jquery-1.11.3.min.js"></script>
"""
if True:
  response = urllib2.urlopen('http://code.jquery.com/jquery-1.11.3.min.js')
  jquery  = "<script type=\"text/javascript\">\n"
  jquery += response.read()
  jquery += "\n</script>\n"



footer="""
</div>
</tt>
</body>
</html>
"""

def formatted_int(i,imax):
  nmax = int(ceil(log10(imax+0.1)))
  n    = int(ceil(log10(i+0.1)))
  val  =""
  for k in range(0,nmax-n):
   val += " "
  val += str(i)
  return val

if len(sys.argv) < 2:
  print "Usage: %s  source.cpp [-o output.html]" % sys.argv[0]
  sys.exit(0)

fin=""
fout=""
i = 1;
while i < len(sys.argv):
  if sys.argv[i] == "-o":
    i += 1;
    fout = sys.argv[i]
  else:
    fin = sys.argv[i]
  i += 1;

if fout == "":
  fout = fin+".html"

print "Highlighting %s" % fin

style='zellner'
style='solarized-light'
cmd='highlight --syntax c++  --include-style --style %s --inline-css -f %s' % (style,fin);
p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out,err = p.communicate()
line_count = 0;
body = out.split('\n')
if body[-1] == "":
  body = body[:-1]
body_anchored = "<code class=\"CodeBody\">\n"
for line in body:
  line_count += 1;
  body_anchored += "<span id=\""+str(line_count)+"\" class=\"codeline\">"+line+"</span>\n"
body_anchored+="</code>"

line_numbers = "<code class=\"LineNumbers\">\n"
total_line_count = line_count;
line_count = 0;
for line in body:
  line_count += 1
  js_line = "onclick=\"keepLocation(window.pageYOffset);\""
  js_line = "class=\"falseLinks\""
#  js_line = ""
  line_numbers += "<a href=\"#%s\" style=\"text-decoration:none\" %s><span style=\"color:#888888;\" class=\"linenumber\">  %s </span></a>\n" % \
    (line_count, js_line, formatted_int(line_count, total_line_count))
line_numbers += "</code>"


size = (int(ceil(log10(total_line_count+0.1)))+2)*8 + 10;
header=header_template % (size,jquery)
print "Writing output to %s" % fout
fout = open(fout, 'w')
fout.write(header+'\n')
fout.write(line_numbers)
fout.write(body_anchored)
fout.write(footer+'\n')
fout.close()
  
     


    
 



  
