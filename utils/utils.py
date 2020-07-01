# 工具类


def line(c="*"):
    """打印一行，用来分割段落"""
    print(c.center(50 - len(c), '-'))


def show(data, info='data to show'):
    print("------ " + info + ":")
    print(data)


def camel_to_underline(camel: str):
    """驼峰转下划线风格"""
    result = camel[0].lower()
    for c in camel[1:]:
        if c.isupper():
            result += '_' + c.lower()
        else:
            result += c
    return result
