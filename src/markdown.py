#coding:utf-8

'''
    使用github api 渲染 markdown 文本
'''

import json
testmd="# 1 \n $$1$$\n *test* \n[image](1.png)\n```lua \n print('hello world')\n```\n"

import requests

def markdown( text, mode='', context='', raw=False):
    url="https://api.github.com/markdown"
    session=requests.session()
    data = {}
    if text:
        data['text'] = text
    if mode in ('markdown', 'gfm'):
        data['mode'] = mode
    if context:
        data['context'] = context
    data=(json.dumps(data))
    req =session.post(url, data)
    if req.ok:
        html = req.text
    return html

print(markdown(testmd))