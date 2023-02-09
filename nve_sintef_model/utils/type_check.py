import os

def get_type_from_dict(d, key, t, default=None, err=False, err_msg=None):
    """
    sjekker om key finnes i dict d

    hvis key ikke eksisterer
       hvis err=True: kast feil melding (err_msg eller default feilmelding om at key ikke fantes)
       hvis err=False: returner default

    hvis key eksisterer
    
    sjekk at datatypen stemmer (med t), hvis ikke gi feil

    ellers returner verdien (da med riktig type)

    """
    x = d.get(key)

    if x == None:

        if err:
            if err_msg != None:
                raise KeyError(err_msg)
            else:
                raise KeyError("Fant ikke key %s" % key)
        else:
            return default

    assert isinstance(x, t), "%s maa vaere type %s" % (key, t)

    return x

def get_path_from_dict(d, key, default=None):
    """
    sjekker om key finnes i dict d

    hvis den ikke eksisterer returneres default

    hvis den eksisterer returneres os.path.abspath
       feiler hvis dette ikke lar seg gjore (eks. hvis verdien ikke er str)

    """
    x = d.get(key)

    if x == None:
        return default

    return os.path.abspath(x)
