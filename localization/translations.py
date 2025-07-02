"""
Translation system for CodeContextor.

This module contains translations for 10 languages and provides
utility functions for accessing translations.
"""

from typing import Dict, List

# Language translations with clean minimal strings
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "EN": {
        "title": "Code Contextor Portable",
        "directory_content": "Files",
        "up_directory": "Up",
        "current_dir": "",
        "select_all": "Select All",
        "clear_selection": "Clear",
        "source_code": "Source Code",
        "save": "Save",
        "copy": "Copy",
        "total_tokens": "Tokens: ",
        "folder": "folder",
        "file_read_error": "Cannot read file: ",
        "folder_read_error": "Cannot read folder: ",
        "root_dir_info": "Already in root directory",
        "root_dir_error": "Cannot go outside root directory",
        "save_success": "Saved to: ",
        "save_error": "Save failed: ",
        "copy_success": "Copied to clipboard!",
        "copy_error": "Copy failed: ",
        "list_error": "Cannot list directory: ",
        "processing": "Processing...",
        "cancel": "Cancel",
        "search_placeholder": "Search...",
        "ignored_items": "Ignored items",
        "show_ignored": "Show ignored",
        "hide_ignored": "Hide ignored",
        
        # Menu items
        "menu_file": "File",
        "menu_select_folder": "Select Folder...",
        "menu_exit": "Exit",
        "menu_version": "Version",
        "menu_about": "About",
        "menu_current_version": "Current Version:",
        
        # Error handling messages
        "error_title": "Error",
        "warning_title": "Warning",
        "info_title": "Information",
        "question_title": "Question",
        "details_label": "Details:",
        
        # Error messages
        "error_file_not_found": "The file could not be found. Please check the path and try again.",
        "error_permission_denied": "Permission denied. You don't have the necessary permissions to access this file or folder.",
        "error_network_connection": "Network connection error. Please check your internet connection and try again.",
        "error_processing_failed": "Processing failed. An error occurred while processing your request.",
        "error_invalid_path": "Invalid path. The specified path is not valid.",
        "error_disk_full": "Disk full. There is not enough space on the disk to complete this operation.",
        "error_memory": "Memory error. The system is running low on memory.",
        "error_timeout": "Operation timed out. The operation took too long to complete.",
        "error_unknown": "An unknown error occurred. Please try again.",
        
        # Warning messages
        "warning_large_file": "This is a large file and may take some time to process.",
        "warning_many_files": "You have selected many files. This operation may take some time.",
        "warning_unsupported_format": "This file format may not be fully supported.",
        "warning_unknown": "An unknown warning occurred.",
        
        # Info messages
        "info_operation_complete": "Operation completed successfully.",
        "info_file_saved": "File saved successfully.",
        "info_copied_clipboard": "Content copied to clipboard.",
        "info_unknown": "Information message.",
        
        # Question messages
        "question_confirm_overwrite": "The file already exists. Do you want to overwrite it?",
        "question_confirm_delete": "Are you sure you want to delete this item?",
        "question_save_changes": "Do you want to save your changes?",
        "question_unknown": "Do you want to continue?"
    },
    "TR": {
        "title": "Code Contextor Portable",
        "directory_content": "Dosyalar",
        "up_directory": "Yukarı",
        "current_dir": "",
        "select_all": "Tümünü Seç",
        "clear_selection": "Temizle",
        "source_code": "Kaynak Kod",
        "save": "Kaydet",
        "copy": "Kopyala",
        "total_tokens": "Token: ",
        "folder": "klasör",
        "file_read_error": "Dosya okunamadı: ",
        "folder_read_error": "Klasör okunamadı: ",
        "root_dir_info": "Zaten kök dizinde",
        "root_dir_error": "Kök dizin dışına çıkılamaz",
        "save_success": "Kaydedildi: ",
        "save_error": "Kayıt başarısız: ",
        "copy_success": "Panoya kopyalandı!",
        "copy_error": "Kopyalama başarısız: ",
        "list_error": "Dizin listelenemedi: ",
        "processing": "İşleniyor...",
        "cancel": "İptal",
        "search_placeholder": "Ara...",
        "ignored_items": "Gizlenen öğeler",
        "show_ignored": "Gizlenenleri göster",
        "hide_ignored": "Gizlenenleri sakla",
        
        # Menu items
        "menu_file": "Dosya",
        "menu_select_folder": "Klasör Seç...",
        "menu_exit": "Çıkış",
        "menu_version": "Sürüm",
        "menu_about": "Hakkında",
        "menu_current_version": "Mevcut Sürüm:",
        
        # Error handling messages
        "error_title": "Hata",
        "warning_title": "Uyarı",
        "info_title": "Bilgi",
        "question_title": "Soru",
        "details_label": "Detaylar:",
        
        # Error messages
        "error_file_not_found": "Dosya bulunamadı. Lütfen yolu kontrol edin ve tekrar deneyin.",
        "error_permission_denied": "Erişim reddedildi. Bu dosya veya klasöre erişim izniniz yok.",
        "error_network_connection": "Ağ bağlantı hatası. İnternet bağlantınızı kontrol edin ve tekrar deneyin.",
        "error_processing_failed": "İşlem başarısız. İsteğiniz işlenirken bir hata oluştu.",
        "error_invalid_path": "Geçersiz yol. Belirtilen yol geçersiz.",
        "error_disk_full": "Disk dolu. Bu işlemi tamamlamak için yeterli disk alanı yok.",
        "error_memory": "Bellek hatası. Sistem belleği yetersiz.",
        "error_timeout": "İşlem zaman aşımına uğradı. İşlem tamamlanması çok uzun sürdü.",
        "error_unknown": "Bilinmeyen bir hata oluştu. Lütfen tekrar deneyin.",
        
        # Warning messages
        "warning_large_file": "Bu büyük bir dosya ve işlenmesi zaman alabilir.",
        "warning_many_files": "Çok sayıda dosya seçtiniz. Bu işlem zaman alabilir.",
        "warning_unsupported_format": "Bu dosya formatı tam olarak desteklenmeyebilir.",
        "warning_unknown": "Bilinmeyen bir uyarı oluştu.",
        
        # Info messages
        "info_operation_complete": "İşlem başarıyla tamamlandı.",
        "info_file_saved": "Dosya başarıyla kaydedildi.",
        "info_copied_clipboard": "İçerik panoya kopyalandı.",
        "info_unknown": "Bilgi mesajı.",
        
        # Question messages
        "question_confirm_overwrite": "Dosya zaten mevcut. Üzerine yazmak istiyor musunuz?",
        "question_confirm_delete": "Bu öğeyi silmek istediğinizden emin misiniz?",
        "question_save_changes": "Değişikliklerinizi kaydetmek istiyor musunuz?",
        "question_unknown": "Devam etmek istiyor musunuz?"
    },
    "RU": {
        "title": "Code Contextor Portable",
        "directory_content": "Файлы",
        "up_directory": "Вверх",
        "current_dir": "",
        "select_all": "Выбрать все",
        "clear_selection": "Очистить",
        "source_code": "Исходный код",
        "save": "Сохранить",
        "copy": "Копировать",
        "total_tokens": "Токены: ",
        "folder": "папка",
        "file_read_error": "Не удалось прочитать файл: ",
        "folder_read_error": "Не удалось прочитать папку: ",
        "root_dir_info": "Уже в корневом каталоге",
        "root_dir_error": "Нельзя выйти за пределы корневого каталога",
        "save_success": "Сохранено в: ",
        "save_error": "Ошибка сохранения: ",
        "copy_success": "Скопировано в буфер обмена!",
        "copy_error": "Ошибка копирования: ",
        "list_error": "Не удалось получить список: ",
        "processing": "Обработка...",
        "cancel": "Отмена",
        "search_placeholder": "Поиск...",
        "ignored_items": "Скрытые элементы",
        "show_ignored": "Показать скрытые",
        "hide_ignored": "Скрыть скрытые",
        
        # Menu items
        "menu_file": "Файл",
        "menu_select_folder": "Выбрать папку...",
        "menu_exit": "Выход",
        "menu_version": "Версия",
        "menu_about": "О программе",
        "menu_current_version": "Текущая версия:",
        
        # Error handling messages
        "error_title": "Ошибка",
        "warning_title": "Предупреждение",
        "info_title": "Информация",
        "question_title": "Вопрос",
        "details_label": "Детали:",
        
        # Error messages
        "error_file_not_found": "Файл не найден. Проверьте путь и попробуйте снова.",
        "error_permission_denied": "Доступ запрещен. У вас нет прав доступа к этому файлу или папке.",
        "error_network_connection": "Ошибка сетевого соединения. Проверьте подключение к интернету и попробуйте снова.",
        "error_processing_failed": "Обработка не удалась. Произошла ошибка при обработке вашего запроса.",
        "error_invalid_path": "Неверный путь. Указанный путь недействителен.",
        "error_disk_full": "Диск заполнен. Недостаточно места на диске для завершения операции.",
        "error_memory": "Ошибка памяти. В системе недостаточно памяти.",
        "error_timeout": "Время операции истекло. Операция заняла слишком много времени.",
        "error_unknown": "Произошла неизвестная ошибка. Попробуйте снова.",
        
        # Warning messages
        "warning_large_file": "Это большой файл, обработка может занять некоторое время.",
        "warning_many_files": "Вы выбрали много файлов. Эта операция может занять некоторое время.",
        "warning_unsupported_format": "Этот формат файла может не полностью поддерживаться.",
        "warning_unknown": "Произошло неизвестное предупреждение.",
        
        # Info messages
        "info_operation_complete": "Операция успешно завершена.",
        "info_file_saved": "Файл успешно сохранен.",
        "info_copied_clipboard": "Содержимое скопировано в буфер обмена.",
        "info_unknown": "Информационное сообщение.",
        
        # Question messages
        "question_confirm_overwrite": "Файл уже существует. Хотите перезаписать его?",
        "question_confirm_delete": "Вы уверены, что хотите удалить этот элемент?",
        "question_save_changes": "Хотите сохранить изменения?",
        "question_unknown": "Хотите продолжить?"
    },
    "ES": {
        "title": "Code Contextor Portable",
        "directory_content": "Archivos",
        "up_directory": "Arriba",
        "current_dir": "",
        "select_all": "Seleccionar todo",
        "clear_selection": "Limpiar",
        "source_code": "Código fuente",
        "save": "Guardar",
        "copy": "Copiar",
        "total_tokens": "Tokens: ",
        "folder": "carpeta",
        "file_read_error": "No se puede leer el archivo: ",
        "folder_read_error": "No se puede leer la carpeta: ",
        "root_dir_info": "Ya en directorio raíz",
        "root_dir_error": "No se puede salir del directorio raíz",
        "save_success": "Guardado en: ",
        "save_error": "Error al guardar: ",
        "copy_success": "¡Copiado al portapapeles!",
        "copy_error": "Error al copiar: ",
        "list_error": "No se puede listar el directorio: ",
        "processing": "Procesando...",
        "cancel": "Cancelar",
        "search_placeholder": "Buscar...",
        "ignored_items": "Elementos ignorados",
        "show_ignored": "Mostrar ignorados",
        "hide_ignored": "Ocultar ignorados",
        
        # Menu items
        "menu_file": "Archivo",
        "menu_select_folder": "Seleccionar Carpeta...",
        "menu_exit": "Salir",
        "menu_version": "Versión",
        "menu_about": "Acerca de",
        "menu_current_version": "Versión Actual:",
        
        # Error handling messages
        "error_title": "Error",
        "warning_title": "Advertencia",
        "info_title": "Información",
        "question_title": "Pregunta",
        "details_label": "Detalles:",
        
        # Error messages
        "error_file_not_found": "No se pudo encontrar el archivo. Compruebe la ruta e inténtelo de nuevo.",
        "error_permission_denied": "Permiso denegado. No tiene los permisos necesarios para acceder a este archivo o carpeta.",
        "error_network_connection": "Error de conexión de red. Compruebe su conexión a internet e inténtelo de nuevo.",
        "error_processing_failed": "El procesamiento falló. Ocurrió un error al procesar su solicitud.",
        "error_invalid_path": "Ruta inválida. La ruta especificada no es válida.",
        "error_disk_full": "Disco lleno. No hay suficiente espacio en el disco para completar esta operación.",
        "error_memory": "Error de memoria. El sistema se está quedando sin memoria.",
        "error_timeout": "La operación expiró. La operación tardó demasiado en completarse.",
        "error_unknown": "Ocurrió un error desconocido. Inténtelo de nuevo.",
        
        # Warning messages
        "warning_large_file": "Este es un archivo grande y puede tardar algún tiempo en procesarse.",
        "warning_many_files": "Ha seleccionado muchos archivos. Esta operación puede tardar algún tiempo.",
        "warning_unsupported_format": "Este formato de archivo puede no ser totalmente compatible.",
        "warning_unknown": "Ocurrió una advertencia desconocida.",
        
        # Info messages
        "info_operation_complete": "Operación completada exitosamente.",
        "info_file_saved": "Archivo guardado exitosamente.",
        "info_copied_clipboard": "Contenido copiado al portapapeles.",
        "info_unknown": "Mensaje informativo.",
        
        # Question messages
        "question_confirm_overwrite": "El archivo ya existe. ¿Desea sobrescribirlo?",
        "question_confirm_delete": "¿Está seguro de que desea eliminar este elemento?",
        "question_save_changes": "¿Desea guardar sus cambios?",
        "question_unknown": "¿Desea continuar?"
    },
    "PT": {
        "title": "Code Contextor Portable",
        "directory_content": "Arquivos",
        "up_directory": "Acima",
        "current_dir": "",
        "select_all": "Selecionar tudo",
        "clear_selection": "Limpar",
        "source_code": "Código fonte",
        "save": "Salvar",
        "copy": "Copiar",
        "total_tokens": "Tokens: ",
        "folder": "pasta",
        "file_read_error": "Não é possível ler o arquivo: ",
        "folder_read_error": "Não é possível ler a pasta: ",
        "root_dir_info": "Já no diretório raiz",
        "root_dir_error": "Não é possível sair do diretório raiz",
        "save_success": "Salvo em: ",
        "save_error": "Erro ao salvar: ",
        "copy_success": "Copiado para a área de transferência!",
        "copy_error": "Erro ao copiar: ",
        "list_error": "Não é possível listar o diretório: ",
        "processing": "Processando...",
        "cancel": "Cancelar",
        "search_placeholder": "Pesquisar...",
        "ignored_items": "Itens ignorados",
        "show_ignored": "Mostrar ignorados",
        "hide_ignored": "Ocultar ignorados",
        
        # Menu items
        "menu_file": "Arquivo",
        "menu_select_folder": "Selecionar Pasta...",
        "menu_exit": "Sair",
        "menu_version": "Versão",
        "menu_about": "Sobre",
        "menu_current_version": "Versão Atual:",
        
        # Error handling messages
        "error_title": "Erro",
        "warning_title": "Aviso",
        "info_title": "Informação",
        "question_title": "Pergunta",
        "details_label": "Detalhes:",
        
        # Error messages
        "error_file_not_found": "O arquivo não foi encontrado. Verifique o caminho e tente novamente.",
        "error_permission_denied": "Permissão negada. Você não tem as permissões necessárias para acessar este arquivo ou pasta.",
        "error_network_connection": "Erro de conexão de rede. Verifique sua conexão com a internet e tente novamente.",
        "error_processing_failed": "O processamento falhou. Ocorreu um erro ao processar sua solicitação.",
        "error_invalid_path": "Caminho inválido. O caminho especificado não é válido.",
        "error_disk_full": "Disco cheio. Não há espaço suficiente no disco para completar esta operação.",
        "error_memory": "Erro de memória. O sistema está com pouca memória.",
        "error_timeout": "A operação expirou. A operação demorou muito para ser concluída.",
        "error_unknown": "Ocorreu um erro desconhecido. Tente novamente.",
        
        # Warning messages
        "warning_large_file": "Este é um arquivo grande e pode levar algum tempo para processar.",
        "warning_many_files": "Você selecionou muitos arquivos. Esta operação pode levar algum tempo.",
        "warning_unsupported_format": "Este formato de arquivo pode não ser totalmente suportado.",
        "warning_unknown": "Ocorreu um aviso desconhecido.",
        
        # Info messages
        "info_operation_complete": "Operação concluída com sucesso.",
        "info_file_saved": "Arquivo salvo com sucesso.",
        "info_copied_clipboard": "Conteúdo copiado para a área de transferência.",
        "info_unknown": "Mensagem informativa.",
        
        # Question messages
        "question_confirm_overwrite": "O arquivo já existe. Deseja sobrescrever?",
        "question_confirm_delete": "Tem certeza de que deseja excluir este item?",
        "question_save_changes": "Deseja salvar suas alterações?",
        "question_unknown": "Deseja continuar?"
    },
    "FR": {
        "title": "Code Contextor Portable",
        "directory_content": "Fichiers",
        "up_directory": "Haut",
        "current_dir": "",
        "select_all": "Tout sélectionner",
        "clear_selection": "Effacer",
        "source_code": "Code source",
        "save": "Enregistrer",
        "copy": "Copier",
        "total_tokens": "Tokens: ",
        "folder": "dossier",
        "file_read_error": "Impossible de lire le fichier: ",
        "folder_read_error": "Impossible de lire le dossier: ",
        "root_dir_info": "Déjà dans le répertoire racine",
        "root_dir_error": "Impossible de sortir du répertoire racine",
        "save_success": "Enregistré dans: ",
        "save_error": "Erreur de sauvegarde: ",
        "copy_success": "Copié dans le presse-papiers!",
        "copy_error": "Erreur de copie: ",
        "list_error": "Impossible de lister le répertoire: ",
        "processing": "Traitement...",
        "cancel": "Annuler",
        "search_placeholder": "Rechercher...",
        "ignored_items": "Éléments ignorés",
        "show_ignored": "Afficher ignorés",
        "hide_ignored": "Masquer ignorés",
        
        # Menu items
        "menu_file": "Fichier",
        "menu_select_folder": "Sélectionner Dossier...",
        "menu_exit": "Quitter",
        "menu_version": "Version",
        "menu_about": "À propos",
        "menu_current_version": "Version Actuelle:",
        
        # Error handling messages
        "error_title": "Erreur",
        "warning_title": "Avertissement",
        "info_title": "Information",
        "question_title": "Question",
        "details_label": "Détails:",
        
        # Error messages
        "error_file_not_found": "Le fichier n'a pas pu être trouvé. Vérifiez le chemin et réessayez.",
        "error_permission_denied": "Permission refusée. Vous n'avez pas les permissions nécessaires pour accéder à ce fichier ou dossier.",
        "error_network_connection": "Erreur de connexion réseau. Vérifiez votre connexion internet et réessayez.",
        "error_processing_failed": "Le traitement a échoué. Une erreur s'est produite lors du traitement de votre demande.",
        "error_invalid_path": "Chemin invalide. Le chemin spécifié n'est pas valide.",
        "error_disk_full": "Disque plein. Il n'y a pas assez d'espace sur le disque pour terminer cette opération.",
        "error_memory": "Erreur de mémoire. Le système manque de mémoire.",
        "error_timeout": "L'opération a expiré. L'opération a pris trop de temps à se terminer.",
        "error_unknown": "Une erreur inconnue s'est produite. Veuillez réessayer.",
        
        # Warning messages
        "warning_large_file": "Il s'agit d'un gros fichier et le traitement peut prendre du temps.",
        "warning_many_files": "Vous avez sélectionné de nombreux fichiers. Cette opération peut prendre du temps.",
        "warning_unsupported_format": "Ce format de fichier peut ne pas être entièrement pris en charge.",
        "warning_unknown": "Un avertissement inconnu s'est produit.",
        
        # Info messages
        "info_operation_complete": "Opération terminée avec succès.",
        "info_file_saved": "Fichier enregistré avec succès.",
        "info_copied_clipboard": "Contenu copié dans le presse-papiers.",
        "info_unknown": "Message informatif.",
        
        # Question messages
        "question_confirm_overwrite": "Le fichier existe déjà. Voulez-vous l'écraser?",
        "question_confirm_delete": "Êtes-vous sûr de vouloir supprimer cet élément?",
        "question_save_changes": "Voulez-vous enregistrer vos modifications?",
        "question_unknown": "Voulez-vous continuer?"
    },
    "IT": {
        "title": "Code Contextor Portable",
        "directory_content": "File",
        "up_directory": "Su",
        "current_dir": "",
        "select_all": "Seleziona tutto",
        "clear_selection": "Cancella",
        "source_code": "Codice sorgente",
        "save": "Salva",
        "copy": "Copia",
        "total_tokens": "Token: ",
        "folder": "cartella",
        "file_read_error": "Impossibile leggere il file: ",
        "folder_read_error": "Impossibile leggere la cartella: ",
        "root_dir_info": "Già nella directory radice",
        "root_dir_error": "Impossibile uscire dalla directory radice",
        "save_success": "Salvato in: ",
        "save_error": "Errore di salvataggio: ",
        "copy_success": "Copiato negli appunti!",
        "copy_error": "Errore di copia: ",
        "list_error": "Impossibile elencare la directory: ",
        "processing": "Elaborazione...",
        "cancel": "Annulla",
        "search_placeholder": "Cerca...",
        "ignored_items": "Elementi ignorati",
        "show_ignored": "Mostra ignorati",
        "hide_ignored": "Nascondi ignorati",
        
        # Menu items
        "menu_file": "File",
        "menu_select_folder": "Seleziona Cartella...",
        "menu_exit": "Esci",
        "menu_version": "Versione",
        "menu_about": "Informazioni",
        "menu_current_version": "Versione Corrente:",
        
        # Error handling messages
        "error_title": "Errore",
        "warning_title": "Avvertimento",
        "info_title": "Informazione",
        "question_title": "Domanda",
        "details_label": "Dettagli:",
        
        # Error messages
        "error_file_not_found": "Il file non è stato trovato. Controlla il percorso e riprova.",
        "error_permission_denied": "Permesso negato. Non hai i permessi necessari per accedere a questo file o cartella.",
        "error_network_connection": "Errore di connessione di rete. Controlla la tua connessione internet e riprova.",
        "error_processing_failed": "L'elaborazione è fallita. Si è verificato un errore durante l'elaborazione della tua richiesta.",
        "error_invalid_path": "Percorso non valido. Il percorso specificato non è valido.",
        "error_disk_full": "Disco pieno. Non c'è abbastanza spazio sul disco per completare questa operazione.",
        "error_memory": "Errore di memoria. Il sistema ha poca memoria disponibile.",
        "error_timeout": "L'operazione è scaduta. L'operazione ha impiegato troppo tempo per completarsi.",
        "error_unknown": "Si è verificato un errore sconosciuto. Riprova.",
        
        # Warning messages
        "warning_large_file": "Questo è un file grande e potrebbe richiedere del tempo per essere elaborato.",
        "warning_many_files": "Hai selezionato molti file. Questa operazione potrebbe richiedere del tempo.",
        "warning_unsupported_format": "Questo formato di file potrebbe non essere completamente supportato.",
        "warning_unknown": "Si è verificato un avvertimento sconosciuto.",
        
        # Info messages
        "info_operation_complete": "Operazione completata con successo.",
        "info_file_saved": "File salvato con successo.",
        "info_copied_clipboard": "Contenuto copiato negli appunti.",
        "info_unknown": "Messaggio informativo.",
        
        # Question messages
        "question_confirm_overwrite": "Il file esiste già. Vuoi sovrascriverlo?",
        "question_confirm_delete": "Sei sicuro di voler eliminare questo elemento?",
        "question_save_changes": "Vuoi salvare le tue modifiche?",
        "question_unknown": "Vuoi continuare?"
    },
    "UA": {
        "title": "Code Contextor Portable",
        "directory_content": "Файли",
        "up_directory": "Вгору",
        "current_dir": "",
        "select_all": "Вибрати все",
        "clear_selection": "Очистити",
        "source_code": "Вихідний код",
        "save": "Зберегти",
        "copy": "Копіювати",
        "total_tokens": "Токени: ",
        "folder": "папка",
        "file_read_error": "Неможливо прочитати файл: ",
        "folder_read_error": "Неможливо прочитати папку: ",
        "root_dir_info": "Вже в кореневому каталозі",
        "root_dir_error": "Неможливо вийти за межі кореневого каталогу",
        "save_success": "Збережено в: ",
        "save_error": "Помилка збереження: ",
        "copy_success": "Скопійовано в буфер обміну!",
        "copy_error": "Помилка копіювання: ",
        "list_error": "Неможливо отримати список каталогу: ",
        "processing": "Обробка...",
        "cancel": "Скасувати",
        "search_placeholder": "Пошук...",
        "ignored_items": "Проігноровані елементи",
        "show_ignored": "Показати проігноровані",
        "hide_ignored": "Сховати проігноровані",
        
        # Menu items
        "menu_file": "Файл",
        "menu_select_folder": "Вибрати папку...",
        "menu_exit": "Вихід",
        "menu_version": "Версія",
        "menu_about": "Про програму",
        "menu_current_version": "Поточна версія:",
        
        # Error handling messages
        "error_title": "Помилка",
        "warning_title": "Попередження",
        "info_title": "Інформація",
        "question_title": "Питання",
        "details_label": "Деталі:",
        
        # Error messages
        "error_file_not_found": "Файл не знайдено. Перевірте шлях і спробуйте знову.",
        "error_permission_denied": "Доступ заборонено. У вас немає необхідних дозволів для доступу до цього файлу або папки.",
        "error_network_connection": "Помилка мережевого з'єднання. Перевірте підключення до інтернету і спробуйте знову.",
        "error_processing_failed": "Обробка не вдалася. Сталася помилка під час обробки вашого запиту.",
        "error_invalid_path": "Недійсний шлях. Вказаний шлях недійсний.",
        "error_disk_full": "Диск заповнений. Недостатньо місця на диску для завершення цієї операції.",
        "error_memory": "Помилка пам'яті. В системі недостатньо пам'яті.",
        "error_timeout": "Час операції вичерпано. Операція зайняла занадто багато часу.",
        "error_unknown": "Сталася невідома помилка. Спробуйте знову.",
        
        # Warning messages
        "warning_large_file": "Це великий файл і обробка може зайняти деякий час.",
        "warning_many_files": "Ви вибрали багато файлів. Ця операція може зайняти деякий час.",
        "warning_unsupported_format": "Цей формат файлу може не повністю підтримуватися.",
        "warning_unknown": "Сталося невідоме попередження.",
        
        # Info messages
        "info_operation_complete": "Операція успішно завершена.",
        "info_file_saved": "Файл успішно збережено.",
        "info_copied_clipboard": "Вміст скопійовано в буфер обміну.",
        "info_unknown": "Інформаційне повідомлення.",
        
        # Question messages
        "question_confirm_overwrite": "Файл уже існує. Хочете перезаписати його?",
        "question_confirm_delete": "Ви впевнені, що хочете видалити цей елемент?",
        "question_save_changes": "Хочете зберегти зміни?",
        "question_unknown": "Хочете продовжити?"
    },
    "DE": {
        "title": "Code Contextor Portable",
        "directory_content": "Dateien",
        "up_directory": "Hoch",
        "current_dir": "",
        "select_all": "Alle auswählen",
        "clear_selection": "Löschen",
        "source_code": "Quellcode",
        "save": "Speichern",
        "copy": "Kopieren",
        "total_tokens": "Token: ",
        "folder": "ordner",
        "file_read_error": "Datei kann nicht gelesen werden: ",
        "folder_read_error": "Ordner kann nicht gelesen werden: ",
        "root_dir_info": "Bereits im Stammverzeichnis",
        "root_dir_error": "Kann Stammverzeichnis nicht verlassen",
        "save_success": "Gespeichert in: ",
        "save_error": "Speicherfehler: ",
        "copy_success": "In die Zwischenablage kopiert!",
        "copy_error": "Kopierfehler: ",
        "list_error": "Verzeichnis kann nicht aufgelistet werden: ",
        "processing": "Verarbeitung...",
        "cancel": "Abbrechen",
        "search_placeholder": "Suchen...",
        "ignored_items": "Ignorierte Elemente",
        "show_ignored": "Ignorierte anzeigen",
        "hide_ignored": "Ignorierte verbergen",
        
        # Menu items
        "menu_file": "Datei",
        "menu_select_folder": "Ordner auswählen...",
        "menu_exit": "Beenden",
        "menu_version": "Version",
        "menu_about": "Über",
        "menu_current_version": "Aktuelle Version:",
        
        # Error handling messages
        "error_title": "Fehler",
        "warning_title": "Warnung",
        "info_title": "Information",
        "question_title": "Frage",
        "details_label": "Details:",
        
        # Error messages
        "error_file_not_found": "Die Datei konnte nicht gefunden werden. Überprüfen Sie den Pfad und versuchen Sie es erneut.",
        "error_permission_denied": "Zugriff verweigert. Sie haben nicht die erforderlichen Berechtigungen für den Zugriff auf diese Datei oder diesen Ordner.",
        "error_network_connection": "Netzwerkverbindungsfehler. Überprüfen Sie Ihre Internetverbindung und versuchen Sie es erneut.",
        "error_processing_failed": "Verarbeitung fehlgeschlagen. Bei der Verarbeitung Ihrer Anfrage ist ein Fehler aufgetreten.",
        "error_invalid_path": "Ungültiger Pfad. Der angegebene Pfad ist nicht gültig.",
        "error_disk_full": "Festplatte voll. Es ist nicht genügend Speicherplatz auf der Festplatte vorhanden, um diesen Vorgang abzuschließen.",
        "error_memory": "Speicherfehler. Dem System geht der Arbeitsspeicher aus.",
        "error_timeout": "Vorgang abgelaufen. Der Vorgang hat zu lange gedauert.",
        "error_unknown": "Ein unbekannter Fehler ist aufgetreten. Versuchen Sie es erneut.",
        
        # Warning messages
        "warning_large_file": "Dies ist eine große Datei und die Verarbeitung kann einige Zeit dauern.",
        "warning_many_files": "Sie haben viele Dateien ausgewählt. Dieser Vorgang kann einige Zeit dauern.",
        "warning_unsupported_format": "Dieses Dateiformat wird möglicherweise nicht vollständig unterstützt.",
        "warning_unknown": "Eine unbekannte Warnung ist aufgetreten.",
        
        # Info messages
        "info_operation_complete": "Vorgang erfolgreich abgeschlossen.",
        "info_file_saved": "Datei erfolgreich gespeichert.",
        "info_copied_clipboard": "Inhalt in die Zwischenablage kopiert.",
        "info_unknown": "Informationsnachricht.",
        
        # Question messages
        "question_confirm_overwrite": "Die Datei existiert bereits. Möchten Sie sie überschreiben?",
        "question_confirm_delete": "Sind Sie sicher, dass Sie dieses Element löschen möchten?",
        "question_save_changes": "Möchten Sie Ihre Änderungen speichern?",
        "question_unknown": "Möchten Sie fortfahren?"
    },
    "NL": {
        "title": "Code Contextor Portable",
        "directory_content": "Bestanden",
        "up_directory": "Omhoog",
        "current_dir": "",
        "select_all": "Alles selecteren",
        "clear_selection": "Wissen",
        "source_code": "Broncode",
        "save": "Opslaan",
        "copy": "Kopiëren",
        "total_tokens": "Tokens: ",
        "folder": "map",
        "file_read_error": "Kan bestand niet lezen: ",
        "folder_read_error": "Kan map niet lezen: ",
        "root_dir_info": "Al in hoofdmap",
        "root_dir_error": "Kan hoofdmap niet verlaten",
        "save_success": "Opgeslagen in: ",
        "save_error": "Fout bij opslaan: ",
        "copy_success": "Gekopieerd naar klembord!",
        "copy_error": "Fout bij kopiëren: ",
        "list_error": "Kan map niet weergeven: ",
        "processing": "Verwerken...",
        "cancel": "Annuleren",
        "search_placeholder": "Zoeken...",
        "ignored_items": "Genegeerde items",
        "show_ignored": "Genegeerde tonen",
        "hide_ignored": "Genegeerde verbergen",
        
        # Menu items
        "menu_file": "Bestand",
        "menu_select_folder": "Map selecteren...",
        "menu_exit": "Afsluiten",
        "menu_version": "Versie",
        "menu_about": "Over",
        "menu_current_version": "Huidige Versie:",
        
        # Error handling messages
        "error_title": "Fout",
        "warning_title": "Waarschuwing",
        "info_title": "Informatie",
        "question_title": "Vraag",
        "details_label": "Details:",
        
        # Error messages
        "error_file_not_found": "Het bestand kon niet worden gevonden. Controleer het pad en probeer opnieuw.",
        "error_permission_denied": "Toegang geweigerd. U heeft niet de benodigde machtigingen om toegang te krijgen tot dit bestand of deze map.",
        "error_network_connection": "Netwerkverbindingsfout. Controleer uw internetverbinding en probeer opnieuw.",
        "error_processing_failed": "Verwerking mislukt. Er is een fout opgetreden bij het verwerken van uw verzoek.",
        "error_invalid_path": "Ongeldig pad. Het opgegeven pad is niet geldig.",
        "error_disk_full": "Schijf vol. Er is niet genoeg ruimte op de schijf om deze bewerking te voltooien.",
        "error_memory": "Geheugenfout. Het systeem heeft weinig geheugen.",
        "error_timeout": "Bewerking verlopen. De bewerking duurde te lang om te voltooien.",
        "error_unknown": "Er is een onbekende fout opgetreden. Probeer opnieuw.",
        
        # Warning messages
        "warning_large_file": "Dit is een groot bestand en verwerking kan enige tijd duren.",
        "warning_many_files": "U heeft veel bestanden geselecteerd. Deze bewerking kan enige tijd duren.",
        "warning_unsupported_format": "Dit bestandsformaat wordt mogelijk niet volledig ondersteund.",
        "warning_unknown": "Er is een onbekende waarschuwing opgetreden.",
        
        # Info messages
        "info_operation_complete": "Bewerking succesvol voltooid.",
        "info_file_saved": "Bestand succesvol opgeslagen.",
        "info_copied_clipboard": "Inhoud gekopieerd naar klembord.",
        "info_unknown": "Informatiebericht.",
        
        # Question messages
        "question_confirm_overwrite": "Het bestand bestaat al. Wilt u het overschrijven?",
        "question_confirm_delete": "Weet u zeker dat u dit item wilt verwijderen?",
        "question_save_changes": "Wilt u uw wijzigingen opslaan?",
        "question_unknown": "Wilt u doorgaan?"
    }
}

def get_translation(language: str, key: str, fallback: str = "") -> str:
    """
    Get translation for a specific language and key.
    
    Args:
        language: Language code (e.g., "EN", "TR", "RU").
        key: Translation key.
        fallback: Fallback text if translation not found.
        
    Returns:
        Translated text or fallback if not found.
    """
    if language not in TRANSLATIONS:
        language = "EN"  # Default to English
    
    return TRANSLATIONS[language].get(key, fallback or key)

def get_available_languages() -> List[str]:
    """
    Get list of available language codes.
    
    Returns:
        List of available language codes.
    """
    return list(TRANSLATIONS.keys())

def is_language_supported(language: str) -> bool:
    """
    Check if a language is supported.
    
    Args:
        language: Language code to check.
        
    Returns:
        True if language is supported, False otherwise.
    """
    return language in TRANSLATIONS 