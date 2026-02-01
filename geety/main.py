import geety
from bs4 import BeautifulSoup as bs


if __name__ == '__main__':
    app = geety.App()
    app.load(open('geety/Components/Card.xml', 'r'))
    app.load(open('geety/index.xml', 'r'))
    app.set_entry_point('App')
    print(bs(app.html(), features='html.parser').prettify())
    #print(app.html())
    #print(app._components)
    #print(app._loaded['Card'].find_by_tag('arg'))
