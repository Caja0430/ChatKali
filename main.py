import openai
import tkinter as tk
import re
import threading
import copy

openai.api_key = "你的api_key，sk-xxxxx"
# print(openai.Model.list())

class ChatApplication(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.history = []
        self.md_code_history = []
        #设置系统提示词
        self.history.append({'role': 'system', 'content': str('我希望你扮演为一个网络安全工程师，将辅助用户使用kali Linux对授权的机器进行合法的渗透测试，请按照渗透测试的先后顺序提出一些问题，一次请只提出一个问题，可以多次提问，你将通过我的反馈收集必要的信息比如：ip、端口、漏洞等信息，辅助我使用kali中的各个工具，如果你要提供命令或指令信息，请用Markdown语法中的代码块包含它，如果你明白我的意思，请开始礼貌后提问')})
        #设置窗口名称
        self.master.title("ChatKali")

    def create_widgets(self):
        # 创建聊天记录框
        self.chat_log = tk.Text(self)
        self.chat_log.pack(side="top", fill="both", expand=True)
        self.chat_log.insert(tk.END, "System: " + "欢迎使用chatkali，开启对话，请发送<开始>"+ "\n")
        self.chat_log.configure(state='disabled')
        
        # 创建用户输入框
        self.user_input = tk.Entry(self)
        self.user_input.pack(side="left", fill="both", expand=True)
        self.user_input.bind("<Return>", self.send_message)

        
        # 创建发送按钮
        self.send_button = tk.Button(self, text="发送", command=self.send_message)
        self.send_button.pack(side="left")
        
        # 创建命令复制框
        self.command_copy = tk.Entry(self)
        self.command_copy.pack(side="left", fill="both", expand=True)
        
        # 创建左右选择按钮
        self.left_button = tk.Button(self, text="<", command=self.move_left)
        self.left_button.pack(side="left")
        self.right_button = tk.Button(self, text=">", command=self.move_right)
        self.right_button.pack(side="left")
        
        # 创建复制按钮
        self.copy_button = tk.Button(self, text="复制", command=self.copy_command)
        self.copy_button.pack(side="left")

    def send_message(self, event=None):
        # 获取用户输入
        user_message = self.user_input.get()
        self.user_input.delete(0, tk.END)

        # 调用openai的API获取回复
        t = threading.Thread(target=self.get_response, args=(user_message,))
        t.start()

    def get_response(self, user_message):
        t = threading.Thread(target=self.get_response_thread, args=(user_message,))
        t.start()

    def get_response_thread(self, user_message):
        if user_message == '':
            tk.messagebox.showwarning('警告', '输入框内容不能为空')
            return
        self.sendList = []
        self.sendList=copy.deepcopy(self.history)
        self.sendList.append({'role': 'user', 'content': user_message})
        print(self.sendList)
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=self.sendList,
            
            max_tokens=500,
            temperature=0,
        )
        print(response)
        # 将聊天记录框设为可编辑状态，插入用户输入和回复
        md_code = re.findall(r'```(.+?)```', str(response.choices[0].message.content), re.S)
        print(md_code)
        self.history.append({'role': 'user', 'content': user_message})
        self.history.append({'role': 'assistant', 'content': str(response.choices[0].message.content)})
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, "You: " + self.history[-2]['content'] + "\n")
        self.chat_log.insert(tk.END, "Chatbot: " + self.history[-1]['content'] + "\n")
        self.chat_log.configure(state='disabled')
        if md_code:
            self.md_code_history.append(md_code[0])
            self.command_copy.delete(0, tk.END)
            self.command_copy.insert(0, self.md_code_history[-1])
            if len(self.md_code_history) == 1:
                self.left_button.config(state='disabled')
                self.right_button.config(state='disabled')
            else:
                self.left_button.config(state='normal')
                self.right_button.config(state='normal')
        else:
            self.left_button.config(state='disabled')
            self.right_button.config(state='disabled')

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
