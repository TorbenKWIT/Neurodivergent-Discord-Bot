# A comprehensive database of common tone indicators used to convey emotional intent in text.

TONE_INDICATORS = {
    "j": {
        "name": "Joking",
        "description": "The statement is a joke and is not meant to be taken seriously.",
        "example": "I'm going to eat this entire raw onion /j"
    },
    "hj": {
        "name": "Half Joking",
        "description": "The statement contains elements of a joke, but has some truth to it.",
        "example": "I need to sleep for three years /hj"
    },
    "s": {
        "name": "Sarcastic / Sarcasm",
        "description": "The statement is sarcastic (saying the opposite of what is meant, often in a mocking tone).",
        "example": "Oh, wonderful! Another rainy day when I planned a picnic /s"
    },
    "srs": {
        "name": "Serious",
        "description": "The statement is completely serious and literal, with no hidden meaning or joking.",
        "example": "I really need someone to talk to right now /srs"
    },
    "nsrs": {
        "name": "Not Serious",
        "description": "The statement is lighthearted or casual, not serious, but not necessarily a joke.",
        "example": "I am obsessed with this song /nsrs"
    },
    "lh": {
        "name": "Lighthearted",
        "description": "The statement is written in a gentle, warm, or friendly tone, without hostility.",
        "example": "Please don't forget to wash your dishes /lh"
    },
    "g": {
        "name": "Genuine / Genuine Question",
        "description": "The writer is asking a sincere question or expressing a sincere thought, without sarcasm or double meaning.",
        "example": "Do you need help with that? /g"
    },
    "gen": {
        "name": "Genuine / Genuine Question",
        "description": "The writer is asking a sincere question or expressing a sincere thought, without sarcasm or double meaning.",
        "example": "You did a fantastic job on this presentation! /gen"
    },
    "nm": {
        "name": "Not Mad",
        "description": "Ensures the reader knows the writer is not angry, irritated, or upset.",
        "example": "Can you please send me that file when you get a chance? /nm"
    },
    "lu": {
        "name": "Little Upset",
        "description": "The writer is feeling slightly upset or hurt, but not extremely angry.",
        "example": "I was looking forward to hanging out today /lu"
    },
    "nf": {
        "name": "Not Forcing",
        "description": "The request or suggestion is optional; the reader is free to decline without pressure.",
        "example": "You should check out this show if you have time /nf"
    },
    "p": {
        "name": "Platonic",
        "description": "The sentiment or affection expressed is purely friendly or platonic, not romantic.",
        "example": "I love you so much, you are the best /p"
    },
    "r": {
        "name": "Romantic",
        "description": "The sentiment or affection expressed has romantic intent.",
        "example": "I can't wait to see you tonight /r"
    },
    "cop": {
        "name": "Coping",
        "description": "The writer is using humor or sarcasm as a coping mechanism for a difficult situation.",
        "example": "Just failed my exam, time to look for a cardboard box to live in /cop"
    },
    "pos": {
        "name": "Positive Connotation",
        "description": "The statement is positive in nature, preventing misinterpretation of ambiguous phrases.",
        "example": "We need to talk later /pos"
    },
    "neg": {
        "name": "Negative Connotation",
        "description": "The statement has a negative context or intent, indicating disappointment or trouble.",
        "example": "We need to talk later /neg"
    },
    "rt": {
        "name": "Rhetorical Question",
        "description": "The question is asked for effect, without expecting an answer.",
        "example": "Who doesn't love a free coffee? /rt"
    },
    "ot": {
        "name": "Off Topic",
        "description": "The message is off-topic relative to the channel's current discussion.",
        "example": "Did anyone see the news today? /ot"
    },
    "q": {
        "name": "Quote",
        "description": "The text is a direct quote from someone else, not the writer's own words.",
        "example": "Be the change you wish to see in the world /q"
    },
    "c": {
        "name": "Copypasta",
        "description": "The message is a copypasta (a block of text copied and pasted from the internet).",
        "example": "Did you ever hear the tragedy of Darth Plagueis the Wise? /c"
    },
    "sx": {
        "name": "Sexual Intent",
        "description": "The statement is intended sexually or contains a sexual double entendre.",
        "example": "I want to eat you up /sx"
    },
    "x": {
        "name": "Sexual Intent",
        "description": "The statement is intended sexually or contains a sexual double entendre.",
        "example": "I want to eat you up /x"
    },
    "nsx": {
        "name": "Non-Sexual Intent",
        "description": "Ensures an ambiguous statement is understood as purely non-sexual.",
        "example": "I can't wait to get in bed /nsx"
    },
    "nx": {
        "name": "Non-Sexual Intent",
        "description": "Ensures an ambiguous statement is understood as purely non-sexual.",
        "example": "I can't wait to get in bed /nx"
    },
    "th": {
        "name": "Threat",
        "description": "The statement is a threat, or is joking about being a threat (use with caution).",
        "example": "I will steal your left shoe if you don't stop /th"
    },
    "cb": {
        "name": "Clickbait",
        "description": "The message is exaggerated or framed like clickbait.",
        "example": "You won't believe what happened to me at the grocery store /cb"
    },
    "ref": {
        "name": "Reference",
        "description": "The message is a reference to a movie, show, meme, or song, rather than literal statement.",
        "example": "Winter is coming /ref"
    },
    "nay": {
        "name": "Not At You",
        "description": "The frustration, anger, or strong emotion expressed in the message is not directed at the reader.",
        "example": "This homework is literally impossible to solve, I hate it /nay"
    },
    "ay": {
        "name": "At You",
        "description": "The emotion or statement in the message is directed at the reader.",
        "example": "I'm really proud of you /ay"
    },
    "nbr": {
        "name": "Not A Brag",
        "description": "The writer is sharing an accomplishment but does not intend to show off or brag.",
        "example": "I finally finished my book today /nbr"
    }
}
