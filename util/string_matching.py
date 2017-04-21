from jellyfish import levenshtein_distance, jaro_winkler
from ngram import NGram


def distance_levenshtein(source_string, comparaison_string):
    """
    Cette methode calcule le porcentage de matching en utilisant la fonction de
    levenshtein

    - La distance de levenshtein messure la difference entre deux chaines en calculant la quantite
    des operations qu'on doit faire au minimun pour transformer une chaine dans l'autre.
    - La distance de levenshtein est toujours au plus la taille du mot plus grand

    :param source_string: le chaine de caracteres qu'on veut comparer
    :param comparaison_string: une autre chaine de caracteres
    :return: le porcentage de matching
    """
    max_distance = max(len(source_string), len(comparaison_string))
    levenshtein = levenshtein_distance(source_string.lower(), comparaison_string.lower())

    return (max_distance - levenshtein) / max_distance


def distance_ngrames(source_string, comparaison_string):
    """
    Cette methode retourne le degre de similarite entre deux chaines en utilisant le methode
    ngram, avec le valeur de N=2

    - La methode de bigrame fait une combination a deux des caracteres sequentiels de chaque
    chaine, et apres compare les couples entre elles pour savoir le niveau du matching
    :param source_string: le chaine de caracteres qu'on veut comparer
    :param comparaison_string: une autre chaine de caracteres
    :return: le pourcentage de matching
    """
    return NGram.compare(source_string.lower(), comparaison_string.lower(), N=2)


def distance_jaro(source_string, comparaison_string):
    """
    Cette methode retourne le degre de similarite en appliquant la methode de Jaro Winkler.

    - La methode de Jaro Winkler, utilise les transpositions sur las lettres differents et la
    taille des mots pour calculer la similarite.

    :param source_string: le chaine de caracteres qu'on veut comparer
    :param comparaison_string: une autre chaine de caracteres
    :return: le pourcentage de matching
    """
    return jaro_winkler(source_string, comparaison_string)




