#!/usr/bin/python
import sys
import os
sys.path.insert(0, os.path.abspath("../../include/"))
import allpairs

canvaswidth = 240
canvasheight = 128

test_template = """<!doctype html>
<!-- This file is generated by build.py. -->
<title>canvas; %s</title>
<link rel="stylesheet" href="../../support/reftests.css">
<style>
 #test > * { %s }
</style>
<div id="test">
 <canvas width=240 height=128></canvas>
</div>
<script>
var c = document.querySelector('canvas').getContext('2d');
var w = c.canvas.width / 2, h = c.canvas.height / 2;
c.fillStyle = 'blue';
c.fillRect(0, 0, w, h);
c.fillRect(w, h, w, h);
c.fillStyle = 'purple';
c.fillRect(w, 0, w, h);
c.fillRect(0, h, w, h);
</script>
"""

ref_template = """<!doctype html>
<!-- This file is generated by build.py. -->
<title>Reference for canvas; %s</title>
<link rel="stylesheet" href="../../support/reftests.css">
<style>
 .helper { overflow:%s }
 .helper > * { %s }
</style>
<div id="ref">
 <span class="helper"><img></span>
</div>
<script>
var c = document.createElement('canvas').getContext('2d');
c.canvas.width = 240;
c.canvas.height = 128;
var w = c.canvas.width / 2, h = c.canvas.height / 2;
c.fillStyle = 'blue';
c.fillRect(0, 0, w, h);
c.fillRect(w, h, w, h);
c.fillStyle = 'purple';
c.fillRect(w, 0, w, h);
c.fillRect(0, h, w, h);
document.querySelector('img').src = c.canvas.toDataURL();
</script>
"""

reftest_list = ''
ref_hashes = {}
for overflow,fit,x,y in allpairs.tests:
    refx = refy = ''
    testx = x
    testy = y

    xx = x
    if x.find('%') != -1:
        xx = x[:-1]
    yy = y
    if y.find('%') != -1:
        yy = y[:-1]

    # reference dimensions
    if fit == 'none':
        refdims = ''
        centerx = 100 - (canvaswidth/2)
        centery = 100 - (canvasheight/2)
    elif fit == 'fill' or fit == 'auto':
        refdims = 'width:200px; height:200px'
        centerx = 0.0
        centery = 0.0
    elif fit == 'cover':
        refdims = 'height:200px'
        centerx = 100 - ((canvaswidth * 200 / canvasheight)/2)
        centery = 0.0
    elif fit == 'contain':
        refdims = 'width:200px'
        centerx = 0.0
        centery = 100 - ((canvasheight * 200 / canvaswidth)/2)
    centerx = 'left:'+str(centerx)+'px'
    centery = 'top:'+str(centery)+'px'

    # reference position
    invalid = False
    # invalid cases use center center
    if ((xx != x or  x in ('1em', '30px', '2cm')) and (y in ('left', 'right')) or
        (yy != y or y in ('1em', '30px', '2cm')) and (x in ('top', 'bottom')) or
        (x == 'top' and y == 'bottom') or (x == 'bottom' and y == 'top') or
        (x == 'left' and y == 'right') or (x == 'right' and y == 'left') or
        x == y == 'left' or x == y == 'right' or x == y == 'top' or x == y == 'bottom'):
        refx = centerx
        refy = centery
        invalid = True
    # valid cases
    else:
        # normalize the order
        if (x in ('top', 'center', 'bottom') and y in ('left' , 'center', 'right')):
            x, y = y, x

        # x
        # center
        if x == '50%' or x == 'center' or x == '':
            refx = centerx
        # left
        elif x == '0%' or x == 'left':
            refx = 'left:0'
        # right
        elif x == '100%' or x == 'right':
            refx = 'right:0'
        # lengths
        elif x == '1em' or x == '30px' or x == '2cm':
            refx = 'left:'+x

        # y
        # center
        if y == '50%' or y == 'center':
            refy = centery
        # top
        elif y == '0%' or y == 'top':
            refy = 'top:0'
        # bottom
        elif y == '100%' or y == 'bottom':
            refy = 'bottom:0'
        # lengths
        elif y == '1em' or y == '30px' or y == '2cm':
            refy = 'top:'+y
        # single keyword
        elif y == '':
            # y value in x
            if x == 'top':
                refx = centerx
                refy = 'top:0'
            elif x == 'bottom':
                refx = centerx
                refy = 'bottom:0'
            # x value in x
            else:
                refy = centery

    test_filename = "%s_%s_%s_%s.html" % (overflow, fit, xx, yy)
    style = "overflow:%s; -o-object-fit:%s; -o-object-position:%s %s" % (overflow, fit, testx, testy)
    if invalid:
        style += " /* INVALID */"
    test_file = open(test_filename, 'w')
    test_file.write(test_template % (style, style))
    test_file.close()
    refstyle = "%s; %s; %s" % (refx, refy, refdims)
    if [v for k, v in ref_hashes.iteritems() if k == overflow+refstyle] == []:
        ref_filename = "%s_%s_%s_%s-ref.html" % (overflow, fit, xx, yy)
        ref_hashes[overflow+refstyle] = ref_filename
        ref_file = open(ref_filename, 'w')
        ref_file.write(ref_template % (style, overflow, refstyle))
        ref_file.close()
    else:
        ref_filename = ref_hashes[overflow+refstyle]
    reftest_list += '== ' + test_filename + ' ' + ref_filename + '\n'
list_file = open('reftest.list', 'w')
list_file.write(reftest_list)
list_file.close()
