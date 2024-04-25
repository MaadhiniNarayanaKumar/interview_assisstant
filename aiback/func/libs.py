import json

def str_json(ans):
    print('hi in libs str::')
    ans1=ans
    if '[' in ans and ']' in ans:
        ans1=ans.split('[')[1].split(']')[0]
    
    print('hi in libs str1::',ans1,type(ans1))
    json_text=json.loads(ans1)
    print('hi in libs str2::',json_text,type(json_text))
    return json_text