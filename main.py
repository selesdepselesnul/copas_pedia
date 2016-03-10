import wikipedia
wikipedia.set_lang('id')
print(wikipedia.page(title='Indonesia').images)
