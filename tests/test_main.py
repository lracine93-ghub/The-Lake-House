from the_lake_house.main import main


def test_main_prints_message(capsys):
    main()
    captured = capsys.readouterr()
    assert "Hello from The Lake House!" in captured.out
