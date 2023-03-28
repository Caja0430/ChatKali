import openai
import tkinter as tk
import re
import threading
import copy
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config.get('openai', 'api_key')
# http代理
proxy = config.get('proxy', 'http_address')
if proxy :
    openai.proxy = proxy
# print(openai.Model.list())

class ChatApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.history = []
        self.md_code_history = []
        # 设置系统提示词
        # self.history.append({'role': 'system', 'content': str('我希望你扮演为一个网络安全工程师，将辅助用户使用kali Linux对授权的机器进行合法的渗透测试，请按照渗透测试的先后顺序提出一些问题，一次请只提出一个问题，可以多次提问，你将通过我的反馈收集必要的信息比如：ip、端口、漏洞等信息，辅助我使用kali中的各个工具，如果你要提供命令或指令信息，最重要的是请把每个命令分别用Markdown语法中的代码块包含，我希望您可以通过我的输入来调整返回的语言,如果你明白我的意思，请开始礼貌提问')})
        # self.history.append({'role': 'system', 'content': str('I would like you to act as a network security engineer and assist the user with conducting legal penetration testing on authorized machines using Kali Linux. Please provide some questions in order of penetration testing, one at a time. You can ask multiple times and I will provide necessary information such as IP address, port, vulnerabilities, etc. through your feedback to help me use various tools in Kali. If you need to provide command or instruction information, please enclose it in a code block using Markdown syntax. I hope you can adjust the language returned based on my input. If you understand what I mean, please begin to ask politely.')})
        self.history.append({'role': 'system', 'content': str(
            'I would like you to role-play as a network security engineer who assists users in conducting authorized penetration testing on machines using Kali Linux. Please provide some questions in the order of penetration testing. Please ask only one question at a time, and you can ask multiple times. I will collect necessary information such as IP addresses, ports, and vulnerabilities through your feedback to assist me in using various tools in Kali. If you need to provide command or instruction information, please wrap each command in a code block using Markdown syntax. I hope you can adjust the language of the responses based on my input. If you understand what I mean, please begin with polite questions.')})

    def create_widgets(self):
        # 创建聊天记录框
        self.chat_log = tk.Text(self, height=20)
        self.chat_log.grid(row=0, column=0, columnspan=6)
        self.chat_log.insert(tk.END, "System: " + "欢迎使用chatkali，开启对话，请发送<开始>" + "\n")
        self.chat_log.insert(tk.END,
                             "System: " + "Welcome to chatkali, to start a conversation, please send <Start>" + "\n")
        self.chat_log.configure(state='disabled')

        # 创建用户输入框
        self.user_input = tk.Entry(self, width=30)
        self.user_input.grid(row=1, column=0)
        self.user_input.bind("<Return>", self.send_message)

        # 创建发送按钮
        self.send_button = tk.Button(self, text="send", command=self.send_message)
        self.send_button.grid(row=1, column=1)

        # 创建命令复制框
        self.command_copy = tk.Entry(self, width=30)
        self.command_copy.grid(row=1, column=2)

        # 创建左右选择按钮
        self.left_button = tk.Button(self, text="<", command=self.move_left)
        self.left_button.grid(row=1, column=3)
        self.right_button = tk.Button(self, text=">", command=self.move_right)
        self.right_button.grid(row=1, column=4)
        self.left_button.config(state='disabled')
        self.right_button.config(state='disabled')

        # 创建复制按钮
        self.copy_button = tk.Button(self, text="copy", command=self.copy_command)
        self.copy_button.grid(row=1, column=5)

        # 设置窗口名称
        self.master.title("ChatKali")

        # 创建状态提示框
        self.status_log = tk.Label(self)
        self.status_log.grid(row=2, column=0, columnspan=6)

        try:
            openai.Model.list()
            self.status_log.config(text="连接openai接口正常，OpenAI interface connection is normal", bg='#c7ffcd')
        except:
            self.status_log.config(text="连接openai接口失败，OpenAI interface connection failed", bg='#ffcccc')

    def send_message(self, event=None):
        self.send_button.config(state='disabled')
        self.status_log.config(text="发送中，Sending...", bg='light gray')
        # 获取用户输入
        user_message = self.user_input.get()
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, "You: " + user_message + "\n")
        self.chat_log.configure(state='disabled')
        self.user_input.delete(0, tk.END)

        # 调用openai的API获取回复
        t = threading.Thread(target=self.get_response, args=(user_message,))
        t.start()

    def get_response(self, user_message):
        t = threading.Thread(target=self.get_response_thread, args=(user_message,))
        t.start()

    def get_response_thread(self, user_message):
        if user_message == '':
            tk.messagebox.showwarning('警告,warn', '输入框内容不能为空,The input box content cannot be empty')
            return
        self.sendList = []
        self.sendList = copy.deepcopy(self.history)
        self.sendList.append({'role': 'user', 'content': user_message})
        print(self.sendList)
        try:
            response = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=self.sendList,

                max_tokens=500,
                temperature=0,
            )
            self.status_log.config(text="获取数据成功，Data retrieval successful", bg='#c7ffcd')
        except:
            self.status_log.config(text="数据发送失败，Data transmission failed", bg='#ffcccc')
        self.send_button.config(state='normal')
        print(response)
        # 将聊天记录框设为可编辑状态，插入用户输入和回复
        md_code = re.findall(r'```\n(.+?)\n```', str(response.choices[0].message.content), re.S)
        print(md_code)
        self.history.append({'role': 'user', 'content': user_message})
        self.history.append({'role': 'assistant', 'content': str(response.choices[0].message.content)})
        self.chat_log.configure(state='normal')
        # self.chat_log.insert(tk.END, "You: " + self.history[-2]['content'] + "\n")
        # 替换掉 代码块
        after_replacement = re.sub(r'^```\n(.*?)\n```$', r'\1', self.history[-1]['content'],
                                   flags=re.MULTILINE | re.DOTALL)
        # print(after_replacement)
        self.chat_log.insert(tk.END, "Chatbot: " + after_replacement + "\n")
        if md_code:
            for code in md_code:
                self.md_code_history.append(code)
            self.command_copy.delete(0, tk.END)
            self.command_copy.insert(0, self.md_code_history[-1])
            if len(self.md_code_history) == 1:
                self.left_button.config(state='disabled')
                self.right_button.config(state='disabled')
            else:
                self.left_button.config(state='normal')
                self.right_button.config(state='normal')
                self.right_button.config(state='disabled')
        else:
            self.left_button.config(state='disabled')
            self.right_button.config(state='disabled')
        self.chat_log.configure(state='disabled')

    def move_left(self):
        if self.md_code_history:
            current_index = self.md_code_history.index(self.command_copy.get())
            if current_index > 0:
                self.command_copy.delete(0, tk.END)
                self.command_copy.insert(0, self.md_code_history[current_index - 1])
                if current_index - 1 == 0:
                    self.left_button.config(state='disabled')
                self.right_button.config(state='normal')

    def move_right(self):
        if self.md_code_history:
            current_index = self.md_code_history.index(self.command_copy.get())
            if current_index < len(self.md_code_history) - 1:
                self.command_copy.delete(0, tk.END)
                self.command_copy.insert(0, self.md_code_history[current_index + 1])
                if current_index + 1 == len(self.md_code_history) - 1:
                    self.right_button.config(state='disabled')
                self.left_button.config(state='normal')

    def copy_command(self):
        command = self.command_copy.get()
        self.clipboard_clear()
        self.clipboard_append(command)
        self.update()

root = tk.Tk()
app = ChatApplication(master=root)
app.mainloop()
