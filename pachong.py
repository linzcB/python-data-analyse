import csv
import re
import requests
from bs4 import BeautifulSoup

# 初始化URL
base_url = "https://scs.bupt.edu.cn/szjs1/jsyl.htm"

# 打开CSV文件以写入模式
with open('teachers_info.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'center', 'name', 'title', 'mentor']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    response = requests.get(base_url)
    response.encoding = 'utf-8'  # 设置编码
    html_content = response.text
    # 解析页面内容
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到中心块
    center_block = soup.find('div', align='center', class_='teacher_div')

    if center_block:
        current_center = None
        teacher_id = 1

        # 英文职称和导师类型的对应中文翻译
        title_translation = {
            'Professor': '教授',
            'Associate Professor': '副教授',
            'Lecturer': '讲师',
            'Researcher': '研究员',
            'Assistant Researcher': '助理研究员'
        }

        mentor_translation = {
            'Supervisor of Doctorate Candidates': '博士生导师',
            'Supervisor of Master\'s Candidates': '硕士生导师'
        }

        # 遍历中心块中的所有元素
        for element in center_block.children:
            if element.name == 'h3':
                # 如果是中心名称
                current_center = element.get_text().strip()
            elif element.name == 'table':
                # 如果是教师信息表
                teacher_links = element.find_all('a', href=True)
                teacher_names = element.find_all('td')

                for teacher_link in teacher_links:
                    teacher_name = teacher_link.get_text().strip()
                    teacher_url = teacher_link['href']

                    try:
                        # 获取教师个人页面内容
                        teacher_response = requests.get(teacher_url)
                        teacher_response.encoding = 'utf-8'
                        teacher_content = teacher_response.text
                        teacher_soup = BeautifulSoup(teacher_content, 'html.parser')
                        content = teacher_soup.get_text()

                        # 检查教师的职称和导师类型
                        title_match = re.search(r'(教授|副教授|讲师|研究员|副研究员|助理研究员|Professor|Associate Professor|Lecturer|Researcher|Assistant Researcher)', content)
                        mentor_type_match = re.search(r'(硕士生导师|博士生导师|博/硕导|Supervisor of Doctorate Candidates|Supervisor of Master\'s Candidates)', content)

                        title = title_match.group(1) if title_match else 'N/A'
                        mentor = mentor_type_match.group(1) if mentor_type_match else 'N/A'

                        # 转换英文职称和导师类型为中文
                        if title in title_translation:
                            title = title_translation[title]
                        if mentor in mentor_translation:
                            mentor = mentor_translation[mentor]

                        # 写入CSV文件
                        writer.writerow({
                            'id': teacher_id,
                            'center': current_center,
                            'name': teacher_name,
                            'title': title,
                            'mentor': mentor
                        })

                        print(f"ID: {teacher_id}, Center: {current_center}, Name: {teacher_name}, Title: {title}, Mentor: {mentor}")
                        teacher_id += 1

                    except requests.RequestException as e:
                        print(f"Failed to fetch {teacher_url}: {e}")
                        continue

                # 处理没有链接的教师
                for teacher_name in teacher_names:
                    if teacher_name.find('a') is None:
                        name = teacher_name.get_text().strip()
                        if name:
                            writer.writerow({
                                'id': teacher_id,
                                'center': current_center,
                                'name': name,
                                'title': 'N/A',
                                'mentor': 'N/A'
                            })
                            print(f"ID: {teacher_id}, Center: {current_center}, Name: {name}, Title: N/A, Mentor: N/A")
                            teacher_id += 1