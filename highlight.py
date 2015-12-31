#!/usr/bin/env python
# $ python highlight.py source.cpp 
# $ chrome open source.cpp.html
# This tool requires "highlight" tool: http://andre-simon.de/index.php

import sys
import subprocess
import urllib2
from math import log10,ceil

header_template="""
<html>
<head>
<style type=text/css> 
a:link {
    background-color: #f8f8f8
}
  
a:hover, a.sftarget {
    background-color: #eef;
}
span:target { 
  background-color: #f6ebbb;
} 
pre { margin: 0; }
div.CodeBox {
  padding:2px;
}
pre.LineNumbers {
  float: left;
  padding-right:0px;
  border: solid 1px #ddd;
  margin-right:0px;
}
span.unselectable {
/*  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none
  user-select: none; 
*/
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

header=header_template % jquery


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

fin=sys.argv[1];
fout=fin+".html"

style='zellner'
style='solarized-light'
cmd='highlight --syntax c++  --include-style --style %s --inline-css -f %s' % (style,fin);
p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out,err = p.communicate()
line_count = 0;
body = out.split('\n')
body_anchored = "<pre>"
for line in body:
  line_count += 1;
  body_anchored += "<span id=\""+str(line_count)+"\"><span class=\"unselectable\"> </span>"+line+"</span>\n"
body_anchored+="</pre>"

line_numbers = "<pre class=\"LineNumbers\">"
total_line_count = line_count;
line_count = 0;
for line in body:
  line_count += 1
  js_line = "onclick=\"keepLocation(window.pageYOffset);\""
  js_line = "class=\"falseLinks\""
#  js_line = ""
  line_numbers += "<a href=\"#%s\" style=\"text-decoration:none\" %s><span style=\"color:#888888;\" >  %s </span></a>\n" % \
    (line_count, js_line, formatted_int(line_count, total_line_count))
line_numbers += "</pre>"


print "Writing output to %s" % fout
fout = open(fout, 'w')
fout.write(header+'\n')
fout.write(line_numbers)
fout.write(body_anchored)
fout.write(footer+'\n')
fout.close()
  
     


    
 



  
