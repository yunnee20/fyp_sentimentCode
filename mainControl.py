import states

states.welcome()

is_ready = states.Ready()

if is_ready:
    answer1 = states.play_question(1)
    answer2 = states.play_question(2)

    print("All answers collected.")
else:
    print("User not ready.")