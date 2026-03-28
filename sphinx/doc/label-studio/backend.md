# Backend_ml 接入

## 后端model加载

模型需要放置在开头，不要放在类里面

## 后端获取图片

下面代码是（我写的）代码中截取的部分，虽然没有变量说明，但大家应该也能看懂吧？

```python
if image_url.startswith('http://') or image_url.startswith('https://'):
    # 通过网络路径直接获取，无auth（看具体情况）
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    img = Image.open(io.BytesIO(response.content))
else:
    # 本地labelstudio获取，要求auth
    full_url = LABEL_STUDIO_HOST.rstrip('/') + image_url
    img = Image.open(requests.get(full_url, headers={'Authorization': f'Token {LABEL_STUDIO_API_KEY}'stream=True).raw)
```

## 返回brush类标注

图像分割brush标注官网没啥资料，我给出一部分代码逻辑，为了篇幅省略了一些异常检测。

```python
# 模型的返回
from label_studio_ml.response import ModelResponse
# Label Studio 转换工具 - 用于 RLE 编码
from label_studio_converter import brush

mask = self._predict_img(img)
image_width, image_height = img.size

# 这玩意似乎有些bug
from_name, to_name, _ = self.get_first_tag_occurence('BrushLabels','Image')
# 这里的标签名称应与 label_config 中定义的标签一致
value = self.parsed_label_config['tag']['labels'][0]
# 为掩码生成 RLE 编码
rle_value = brush.mask2rle(mask)
# 结果必要的一些标签
result = {
    'id': str(uuid4())[:4],
    'type': 'brushlabels',
    'from_name': from_name,
    'to_name': to_name,
    'original_width': image_width,
    'original_height': image_height,
    'image_rotation': 0,
    'value': {
        'format': 'rle',
        'rle': rle_value,
        "brushlabels": [value]  # 这里的标签名称应与 label_config 中定义的标签一致
    },
    'readonly': False
}
# 总体返回的内容
predictions.append({
    'result': [result],
    'model_version': self.get('model_version'),
    'score': self._calculate_prediction_score(mask)
}) 

# 这个就是返回值了
return ModelResponse(predictions=predictions)

```
