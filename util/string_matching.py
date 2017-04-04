from jellyfish import levenshtein_distance, jaro_winkler
from ngram import NGram


def distance_levenshtein(source_string, comparaison_string):
    """
    Cette méthode calcule le porcentage de matching en utilisant la fonction de
    levenshtein

    - La distance de levenshtein messure la difference entre deux chaînes en calculant la quantité
    des operations qu'on doit faire au minimun pour transformer une chaîne dans l'autre.
    - La distance de levenshtein est toujours au plus la taille du mot plus grand

    :param source_string: le chaîne de caractères qu'on veut comparer
    :param comparaison_string: une autre chaîne de caractères
    :return: le porcentage de matching
    """
    max_distance = max(len(source_string), len(comparaison_string))
    levenshtein = levenshtein_distance(source_string.lower(), comparaison_string.lower())

    return (max_distance - levenshtein) / max_distance


def distance_ngrames(source_string, comparaison_string):
    """
    Cette méthode retourne le dégré de similarité entre deux chaînes en utilisant le méthode
    ngram, avec le valeur de N=2

    - La méthode de bigrame fait une combination à deux des caractères sequentiels de chaque
    chaîne, et après compare les couples entre elles pour savoir le niveau du matching
    :param source_string: le chaîne de caractères qu'on veut comparer
    :param comparaison_string: une autre chaîne de caractères
    :return: le porcentage de matching
    """
    return NGram.compare(source_string.lower(), comparaison_string.lower(), N=2)


def distance_jaro(source_string, comparaison_string):
    """
    Cette méthode retourne le degré de similarité en appliquant la méthode de Jaro Winkler.

    - La méthode de Jaro Winkler, utilise les traspositions sur las lettres différents et la
    taille des mots pour calculer la similarité.

    :param source_string: le chaîne de caractères qu'on veut comparer
    :param comparaison_string: une autre chaîne de caractères
    :return: le porcentage de matching
    """
    return jaro_winkler(source_string, comparaison_string)




