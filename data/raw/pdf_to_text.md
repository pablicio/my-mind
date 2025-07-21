| Função                              | O que faz                                                                                     |
| ----------------------------------- | --------------------------------------------------------------------------------------------- |
| `remove_file_with_retry`            | Tenta deletar um arquivo, mesmo que esteja temporariamente em uso (com múltiplas tentativas). |
| `remove_directory_with_retry`       | Remove uma pasta (e conteúdo), com tolerância a erros como bloqueios temporários do sistema.  |
| `remove_error`                      | Handler usado por `shutil.rmtree` para tentar deletar arquivos travados.                      |
| `convert_PDF_to_text(reader, path)` | Converte cada página de um PDF em imagem, aplica OCR (EasyOCR) e retorna o texto extraído.    |
