from anyblok.declarations import Declarations
from anyblok.column import String, Selection


@Declarations.register(Declarations.Model.Pyramid)
class User:
    name = String(nullable=False)
    lang = Selection(selections={'fr': 'Français', 'en': 'English'}, default='fr')
    theme = Selection(
        selections={
            'journal': 'Journal',
            'minthy': 'Minthy',
            'darkly': 'Darkly',
        }, default='minthy')
