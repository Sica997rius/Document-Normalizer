import json
from datetime import datetime
from pathlib import Path
import Classes
import Costants
from CSVReader import CSVReader
from DocumentReader import DocumentReader
from TextReader import TextReader

start = input("Do you want to analyze a folder or search the history? Press Enter or 'y' to normalize, 'n' to search history: ").strip().lower()
while True:
    if start in ["y" , "yes", "si", "", "sì"]:
        start_normalization=True
        if start_normalization:
            print("")
            print("")
            save = None
            document_list = DocumentReader.open_document_list()
            if document_list:
                allowed_files = DocumentReader.allowed_extensions(document_list)
                disallowed_files = DocumentReader.disallowed_extensions(document_list)
                txt_files = DocumentReader.txt_documents(allowed_files)
                csv_files = DocumentReader.csv_documents(allowed_files)
                md_files = DocumentReader.md_documents(allowed_files)
                print("")
                print("The allowed files are the following: ")
                print("")
                print("Text files: ")
                print(txt_files)
                print("")
                print("Data files: ")
                print(csv_files)
                print("")
                print("Markdown files: ")
                print(md_files)
                print("")
                print("The disallowed files are the following: ")
                print(disallowed_files)
                print("")
                session_documents = {}
                save_session = input(
                    "Do you want to apply the changes to the files?\n"
                    "y) yes (Enter)\n"
                    "n) no\n"    
                )
                answer = save_session.strip().lower()
                while True:
                    if answer in ["y", "yes", "s", "si", "sì", ""]:
                        save = True
                        break
                    elif answer in ["n", "no"]:
                        save = False
                        break
                    else:
                        answer = input("Invalid answer. Please type y or n (Enter = y): ").strip().lower()
        
                if not save:
                    print("No file was changed.")
        # if save is true, the system saves the changes for each text file, markdown file and csv file,
        # in a single session in the 'session.json' file.

        # ================= LOOP 1: TEXT FILES (.TXT) =================
        if save:
            if txt_files:
                print("---processing TXT files---")
                for number, (file_name, ext) in txt_files.items():
                    file_path = document_list[number]
                    try:
                        text, is_binary = DocumentReader.read_text(file_path)
                        if text:
                            if is_binary:# if the file is binary, the system does not normalize and autovalorizes atributes with default values.
                                normalized_text = text
                                word_count = 0
                                excerpt = Costants.BINARY_FILE_NOTE
                                detected_date = None
                                title = Path(file_name).stem # Extract the title from the file name excluding the extension
                            else:
                                normalized_text = TextReader.normalize_text(text)
                                if not normalized_text:
                                    print(f"document {file_name} will be skipped because it is empty\n")
                                    normalized_text = text
                                    word_count = 0
                                    excerpt = Costants.FILE_NORMALIZED_EMPTY_NOTE
                                    detected_date = None
                                    title = Path(file_name).stem # Extract the title from the file name excluding the extension
                                    continue
                                normalized_text = TextReader.normalize_text(text)
                                word_count = TextReader.count_words(normalized_text)
                                excerpt = TextReader.create_excerpt(normalized_text)
                                detected_date = TextReader.find_date(normalized_text)
                                title = DocumentReader.title_from_filename(Path(file_name).stem)
                                title = " ".join(word.capitalize() for word in title.strip().split()) #than capitalize the first letter of each word in the title.
                            # after the normalization, the system creates a Document object.
                            doc=Classes.Document(
                                document_id=str(number),
                                new_title=title,
                                original_title=file_name,
                                word_count=word_count,
                                excerpt=excerpt,
                                new_content=normalized_text,
                                format=ext,
                                path=str(file_path),
                                date=detected_date,
                                original_content=text,
                            )
                            print(f"document {number}{file_name} processed successfully: ")
                            print(f"Title:{doc.new_title}")
                            print(f"Word Count:{doc.word_count}")
                            print(f"date:{doc.date}")
                            print(f"excerpt:{doc.excerpt}")

                            changes_description= doc.changes_made
                            new_path= file_path.parent / (doc.new_title + ext)
                            if doc .title_changed:
                                new_path=DocumentReader.unique_path(file_path, new_path)
                                file_path.rename(new_path)
                                doc.path=str(new_path)
                                if new_path.stem!=doc.new_title:
                                    print(f"File '{file_name}' renamed to '{new_path.name}' ('{doc.new_title + ext}' was already taken).")
                            if doc.text_changed:
                                DocumentReader.write_text(new_path, normalized_text)
                                print(f"Content of '{file_name}' updated successfully.")

                            session_documents[str((file_path))] = {
                                "file_name": file_name,
                                "title": doc.new_title,
                                "word_count": doc.word_count,
                                "original_path": str(file_path),
                                "new_path": str(new_path),
                                "changes":[changes_description],
                                "date": doc.date,
                                "excerpt": doc.excerpt
                                }
                            print("-"*50)
                        else:
                            print(f"document {file_name} will be skipped because it is empty\n")
                    except Exception as e:
                        print(f"Error processing document {file_name}: {e}\n")
        # ================= LOOP 2: MARKDOWN FILES (.MD) =================
        if save:
            if md_files:
                print("---processing MD files---")
                for number, (file_name, ext) in md_files.items():
                    file_path = document_list[number]
                    try:
                        text, is_binary = DocumentReader.read_text(file_path)
                        if text:
                            if is_binary:# if the file is binary, the system does not normalize and autovalorizes atributes with default values.
                                normalized_text = text
                                word_count = 0
                                excerpt = Costants.BINARY_FILE_NOTE
                                detected_date = None
                                title = Path(file_name).stem # Extract the title from the file name excluding the extension
                            else:
                                normalized_text = TextReader.normalize_text(text)
                                if not normalized_text:
                                    print(f"document {file_name} will be skipped because it is empty\n")
                                    normalized_text = text
                                    word_count = 0
                                    excerpt = Costants.FILE_NORMALIZED_EMPTY_NOTE
                                    detected_date = None
                                    title = Path(file_name).stem # Extract the title from the file name excluding the extension
                                    continue
                                normalized_text = TextReader.normalize_text(text)
                                word_count = TextReader.count_words(normalized_text)
                                excerpt = TextReader.create_excerpt(normalized_text)
                                detected_date = TextReader.find_date(normalized_text)
                                title = DocumentReader.title_from_filename(Path(file_name).stem)
                                title = " ".join(word.capitalize() for word in title.strip().split()) #than capitalize the first letter of each word in the title.
                            # after the normalization, the system creates a Document object.
                            doc=Classes.Document(
                                document_id=str(number),
                                new_title=title,
                                original_title=file_name,
                                word_count=word_count,
                                excerpt=excerpt,
                                new_content=normalized_text,
                                format=ext,
                                path=str(file_path),
                                date=detected_date,
                                original_content=text,
                            )
                            print(f"document {number}{file_name} processed successfully: ")
                            print(f"Title:{doc.new_title}")
                            print(f"Word Count:{doc.word_count}")
                            print(f"date:{doc.date}")
                            print(f"excerpt:{doc.excerpt}")

                            changes_description= doc.changes_made
                            new_path= file_path.parent / (doc.new_title + ext)
                            if doc .title_changed:
                                new_path=DocumentReader.unique_path(file_path, new_path)
                                file_path.rename(new_path)
                                doc.path=str(new_path)
                                if new_path.stem!=doc.new_title:
                                    print(f"File '{file_name}' renamed to '{new_path.name}' ('{doc.new_title + ext}' was already taken).")
                            if doc.text_changed:
                                DocumentReader.write_text(new_path, normalized_text)
                                print(f"Content of '{file_name}' updated successfully.")

                            session_documents[str((file_path))] = {
                                "file_name": file_name,
                                "title": doc.new_title,
                                "word_count": doc.word_count,
                                "original_path": str(file_path),
                                "new_path": str(new_path),
                                "changes":[changes_description],
                                "date": doc.date,
                                "excerpt": doc.excerpt
                                }
                            print("-"*50)
                        else:
                            print(f"document {file_name} will be skipped because it is empty\n")
                    except Exception as e:
                        print(f"Error processing document {file_name}: {e}\n")
                # ================= LOOP 3: CSV FILES (.CSV) =================
        if save:
            if csv_files:
                print("---processing CSV files---")
                for number, (file_name, ext) in csv_files.items():
                    file_path = document_list[number]
                    try:
                        text, is_binary = DocumentReader.read_text(file_path)
                        if text:
                            if is_binary:# if the file is binary, the system does not normalize and autovalorizes atributes with default values.
                                normalized_text = text
                                word_count = 0
                                excerpt = Costants.BINARY_FILE_NOTE
                                detected_date = None
                                title = Path(file_name).stem # Extract the title from the file name excluding the extension
                            else:
                                normalized_text = CSVReader.normalize_text(text)
                                if not normalized_text:
                                    print(f"document {file_name} will be skipped because it is empty\n")
                                    normalized_text = text
                                    word_count = 0
                                    excerpt = Costants.FILE_NORMALIZED_EMPTY_NOTE
                                    detected_date = None
                                    title = Path(file_name).stem # Extract the title from the file name excluding the extension
                                    continue
                                word_count = TextReader.count_words(normalized_text)
                                excerpt = CSVReader.create_excerpt(normalized_text)
                                detected_date = CSVReader.find_date_from_title(Path(file_name).stem)
                                title = DocumentReader.title_from_filename(Path(file_name).stem)
                                title = " ".join(word.capitalize() for word in title.strip().split()) #than capitalize the first letter of each word in the title.
                            doc=Classes.Document(
                                document_id=str(number),
                                new_title=title,
                                original_title=file_name,
                                word_count=word_count,
                                excerpt=excerpt,
                                new_content=normalized_text,
                                format=ext,
                                path=str(file_path),
                                date=detected_date,
                                original_content=text,
                            )
                            print(f"document {number}{file_name} processed successfully: ")
                            print(f"Title:{doc.new_title}")
                            print(f"Word Count:{doc.word_count}")
                            print(f"date:{doc.date}")
                            print(f"excerpt:{doc.excerpt}")
                            changes_description= doc.changes_made
                            new_path= file_path.parent / (doc.new_title + ext)
                            if doc .title_changed:
                                new_path=DocumentReader.unique_path(file_path, new_path)
                                file_path.rename(new_path)
                                doc.path=str(new_path)
                                if new_path.stem!=doc.new_title:
                                    print(f"File '{file_name}' renamed to '{new_path.name}' ('{doc.new_title + ext}' was already taken).")
                            if doc.text_changed:
                                DocumentReader.write_text(new_path, normalized_text)
                                print(f"Content of '{file_name}' updated successfully.")

                            session_documents[str((file_path))] = {
                                "file_name": file_name,
                                "title": doc.new_title,
                                "word_count": doc.word_count,
                                "original_path": str(file_path),
                                "new_path": str(new_path),
                                "changes":[changes_description],
                                "date": doc.date,
                                "excerpt": doc.excerpt
                                }
                            print("-"*50)
                        else:
                            print(f"document {file_name} will be skipped because it is empty\n")
                    except Exception as e:
                        print(f"Error processing document {file_name}: {e}\n")
                        # Outside the loops: handle the overall saving of the session to a JSON file
        if save and session_documents:
            try:
                temp_session = Classes.Session(session_id=0, session_date=datetime.now())
                news_session_id = temp_session.last_session + 1
                
                session_record = Classes.Session (
                    session_id=news_session_id,
                    session_date=datetime.now(),
                    documents=session_documents
                )
                try:
                    with open("session.json", "r", encoding="utf-8") as f:
                        existing_sessions = json.load(f)
                        if not isinstance(existing_sessions, list):
                            existing_sessions = [existing_sessions]
                except FileNotFoundError:
                    existing_sessions = []
                except json.JSONDecodeError:
                    Costants.SESSION_FILE.replace( Costants.SESSION_FILE.with_name("session_backup.json"))
                    print("The file 'session.json' was damaged: it has been renamed to 'session_backup.json'.")
                    existing_sessions = []
                session_data = {
                    "session_id": session_record.session_id,
                    "session_date": session_record.session_date.isoformat(),
                    "documents": session_record.documents
                }
                existing_sessions.append(session_data)
                with open("session.json", "w", encoding="utf-8") as f:
                    json.dump(existing_sessions, f, ensure_ascii=False, indent=2)
                print(f"Session {session_record.session_id} saved successfully with {len(session_documents)} documents.")
            except Exception as e:
                print(f"Error saving session: {e}")
            pass
        start="n"
    elif start in ["n", "no"]:
        continue_search=True
        # the user can search a word in the history of the sessions. words are searched in title, file_name, original_path, new_path, excerpt, changes, date
        # if a word searched is part of a part of word, system will find it becaue "search_words = search.split()"
        while continue_search:
            search = input("Type the words to search for (or press Enter to skip): ").strip().lower()
            if search:
                search_words = search.split()
                try:
                    with open("session.json", "r", encoding="utf-8") as f:
                        existing_sessions = json.load(f)
                        if not isinstance(existing_sessions, list):
                            existing_sessions = [existing_sessions]
                except FileNotFoundError:
                    print("No session history found.")
                    existing_sessions = []
                except json.JSONDecodeError:
                    existing_sessions = []
                    print("The file 'session.json' is damaged or empty. No session history can be read.")

                results = []
                for session in existing_sessions:
                    for doc_info in session.get("documents", {}).values():
                        title = doc_info.get("title", "").lower()
                        file_name = doc_info.get("file_name", "").lower()
                        original_path = doc_info.get("original_path", "").lower()
                        new_path = doc_info.get("new_path", "").lower()
                        excerpt = doc_info.get("excerpt", "").lower()
                        changes = " ".join(doc_info.get("changes", [])).lower()
                        date = (doc_info.get("date") or "").lower()
                        fields = [title, file_name, original_path, new_path, excerpt, changes, date]

                        #if all elements of search_words are found in any of the fields, the document is added to the results list.
            
                        if all(any(word in field for field in fields) for word in search_words):
                            results.append((session, doc_info))

                if results:
                    print(f"\nDocuments found: {len(results)}\n")
                    for session, doc_data in results:
                        print("-" * 40)
                        print(f"Session {session.get('session_id')} ({session.get('session_date')})")
                        print(f"  Title: {doc_data.get('title')}")
                        print(f"  Original name: {doc_data.get('file_name')}")
                        print(f"  Original path: {doc_data.get('original_path')}")
                        print(f"  Current path: {doc_data.get('new_path')}")
                        print(f"  Changes: {', '.join(doc_data.get('changes', []))}")
                        print(f"  Date found: {doc_data.get('date')}")
                        print(f"  Excerpt: {doc_data.get('excerpt')}")
                else:
                    print("\nNo documents found.")
            else:
                print("No search words entered. Skipping search.")
                continue_search = False
        break
    else:
        start = input("Invalid answer. Please type y or n (Enter = y): ").strip().lower()