# README

## 创建虚拟运行环境

```bash
// 利用venv，创建一个名为venv的虚拟环境
python3 -m venv venv
py -3 -m venv venv  // Windows 下

// 激活虚拟环境
$ . venv/bin/activate
> venv\Scripts\activate     //在 Windows 下

// 激活后，你的终端提示符会显示虚拟环境的名称。
```

## 项目启动

可以使用 flask 命令或者 python 的 -m 开关来运行这个应用。在运行应用之前，需要在终端里导出 FLASK_APP 环境变量:

```bash
$ export FLASK_APP=hello.py
$ flask run
 * Running on http://127.0.0.1:5000/
```

如果是在 Windows 下，那么导出环境变量的语法取决于使用的是哪种命令行解释器。 

```bash
// 在 Command Prompt 下:
C:\path\to\app>set FLASK_APP=hello.py

// 在 PowerShell 下:
PS C:\path\to\app> $env:FLASK_APP = "hello.py"

// 还可以使用 python -m flask:
$ export FLASK_APP=hello.py
$ python -m flask run
 * Running on http://127.0.0.1:5000/
```

## 参考资料
[Flask 快速上手](https://dormousehole.readthedocs.io/en/latest/quickstart.html#id2)