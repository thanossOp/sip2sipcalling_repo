import pvorca

def generate_audio_2(text, filename):
    orca = pvorca.create(
        access_key="89BlxJKCyiH/Eye4zhS74DxMibVpYlj/6qkLLw90NCm+ICw+AKYZqg==",
    )
    orca.synthesize_to_file(text, filename)