import argparse
import json
from datetime import datetime
from pathlib import Path
from . import Classes
from . import Costants
from .CSVReader import CSVReader
from .DocumentReader import DocumentReader
from .TextReader import TextReader

READERS = [TextReader, CSVReader] #Classes used to read and normalize text files, markdown files and csv files

arguments = argparse.ArgumentParser(prog="python -m parser", description="Without a command the program starts the interactive menu.") 
arguments.add_argument("command", nargs="?", choices=["normalize", "search", "list", "stats"])
arguments.add_argument("values", nargs="*", help="normalize: the folder, search: the words")
arguments.add_argument("--yes", action="store_true", help="normalize without asking")
arguments.add_argument("--no", action="store_true", help="normalize: show the files without changing them")
arguments.add_argument("--ext", help="list: only the documents of this format, e.g. csv")
args = arguments.parse_args()

start = {"normalize": "y", "search": "n", "list": "l", "stats": "t"}.get(args.command) or input("Do you want to analyze a folder or search the history? Press Enter or 'y' to normalize, 'n' to search history, 'l' to list documents, 't' for statistics: ").strip().lower()
while True:
    if start in ["y" , "yes", "si", "", "sì"]:
        print("")
        print("")
        save = None
        document_list = DocumentReader.open_document_list(args.values[0] if args.values else None)
        if document_list:
            readers = {ext: reader for reader in READERS for ext in reader.EXTENSIONS} #readers is a dictionary that maps file extensions to their corresponding reader classes.
            allowed_files = DocumentReader.allowed_extensions(document_list, readers)
            disallowed_files = DocumentReader.disallowed_extensions(document_list, readers)
            print("")
            print("The allowed files are the following: ")
            print("")
            for ext in readers:
                print(f"{ext} files: ")
                print(DocumentReader.documents_by_format(allowed_files, ext))
                print("")
            print("The disallowed files are the following: ")
            print(disallowed_files)
            print("")
            session_documents = {}
            if args.yes:
                save_session = "y"
            elif args.no:
                save_session = "n"
            else:
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

        if save:
            discarded = [(file_name, f"extension not allowed ({ext or 'none'})") for file_name, ext in disallowed_files.values()]
            for ext, reader in readers.items():
                files = DocumentReader.documents_by_format(allowed_files, ext)
                if files:
                    print(f"---processing {ext[1:].upper()} files---")
                for number, (file_name, ext) in files.items():
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
                                normalized_text = reader.normalize_text(text)
                                if not normalized_text:
                                    print(f"document {file_name} will be skipped because it is empty\n")
                                    discarded.append((file_name, "empty after normalization"))
                                    continue
                                word_count = reader.count_words(normalized_text)
                                excerpt = reader.create_excerpt(normalized_text)
                                detected_date = reader.get_date(normalized_text, file_name) # normalized_text is used in txt and md files, file_name is used in csv files 
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
                            print(f"document {number} {file_name} processed successfully: ")
                            print(f"Title:{doc.new_title}")
                            print(f"Word Count:{doc.word_count}")
                            print(f"date:{doc.date}")
                            print(f"excerpt:{doc.excerpt}")
                            print(f"format:{doc.format}")
                            print(f"path:{doc.path}")

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
                                "format": doc.format,
                                "excerpt": doc.excerpt
                                }
                            print("-"*50)
                        else:
                            print(f"document {file_name} will be skipped because it is empty\n")
                            discarded.append((file_name, "empty file"))
                    except Exception as e:
                        print(f"Error processing document {file_name}: {e}\n")
                        discarded.append((file_name, f"error: {e}"))
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
        if save:
            print("")
            print(f"Documents processed: {len(session_documents)}")
            print(f"Documents discarded: {len(discarded)}")
            for file_name, reason in discarded:
                print(f"  {file_name}: {reason}")
            print("")
        if args.command:
            break
        start="n"
    elif start in ["n", "no"]:
        continue_search=True
        # the user can search a word in the history of the sessions. words are searched in title, file_name, original_path, new_path, excerpt, changes, date
        # if a word searched is part of a part of word, system will find it becaue "search_words = search.split()"
        while continue_search:
            if args.command == "search":
                search = " ".join(args.values).strip().lower()
                continue_search = False
            else:
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
                        format = doc_info.get("format", "").lower()
                        fields = [title, file_name, original_path, new_path, excerpt, changes, date, format]

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
                        print(f"  Format: {doc_data.get('format')}")
                        print(f"  Excerpt: {doc_data.get('excerpt')}")
                else:
                    print("\nNo documents found.")
            else:
                print("No search words entered. Skipping search.")
                continue_search = False
        break
    elif start in ["l", "list", "t", "stats"]:
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
        documents = {}
        for session in existing_sessions:
            for doc_info in session.get("documents", {}).values():
                documents[doc_info.get("new_path")] = doc_info
        documents = list(documents.values())
        if start in ["l", "list"]:
            formats = ", ".join(ext[1:] for reader in READERS for ext in reader.EXTENSIONS) # formats="txt, md, csv"
            if args.command == "list":
                extension = (args.ext or "").strip().lower().lstrip(".") 
            else:
                extension = input(f"Which format? ({formats}, Enter = all): ").strip().lower().lstrip(".")
            if extension:
                documents = [doc_info for doc_info in documents if doc_info.get("format", "") == "." + extension] 
            if not documents:
                print("No documents found.")
            else:
                print(f"Documents: {len(documents)}")
                for doc_info in sorted(documents, key=lambda x: x.get("format", "")):
                    print(f"  [{doc_info.get('format', '')}] {doc_info.get('title')} | {doc_info.get('word_count')} words | date: {doc_info.get('date')} | {doc_info.get('new_path')}")
        elif not documents:
            print("No documents found.")
        else:
            formats = {} # es. {"txt": 10, "md": 5, "csv": 3}
            for doc_info in documents:
                ext = doc_info.get("format", "")
                formats[ext] = formats.get(ext, 0) + 1 #counts the number of documents for each format
            total_words = sum(doc_info.get("word_count", 0) for doc_info in documents)
            longest = max(documents, key=lambda doc_info: doc_info.get("word_count", 0)) # finds the document with the highest word count
            print("")
            print(f"Sessions: {len(existing_sessions)}") # prints the number of sessions
            print(f"Documents in the archive: {len(documents)}") # prints the total number of documents in the archive
            print("")
            for ext, count in sorted(formats.items()):
                print(f" Documents {ext}: {count}")
            print("")
            print(f"Binary files: {sum(1 for doc_info in documents if doc_info.get('excerpt') == Costants.BINARY_FILE_NOTE)}") #counts the number of binary files in the archive (1)
            print(f"Documents with a date: {sum(1 for doc_info in documents if doc_info.get('date'))}")
            print(f"Total words: {total_words}")
            print(f"Average words per document: {total_words / len(documents):.1f}")
            print(f"Longest document: {longest.get('title')} with {longest.get('word_count')} words ")
        break
    else:
        start = input("Invalid answer. Please type y, n, l or t (Enter = y): ").strip().lower()