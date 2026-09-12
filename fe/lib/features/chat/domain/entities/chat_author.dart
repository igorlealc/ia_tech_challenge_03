enum ChatAuthor {
  doctor,
  assistant;

  String get label {
    return switch (this) {
      ChatAuthor.doctor => 'Medico',
      ChatAuthor.assistant => 'IA',
    };
  }
}
