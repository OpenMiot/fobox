import geety


if __name__ == '__main__':
    app = geety.App()
    app.load(open('geety/Components/Card.xml', 'r'))
    app.set_entry_point('App')
    print(app.html())
    print(app._components)
    #print(app._loaded['Card'].find_by_tag('arg'))
