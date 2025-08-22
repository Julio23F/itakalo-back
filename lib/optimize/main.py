# import sys
# from objsplit import generateOptimizedData 

# if __name__ == "__main__": 
#   # Arguments de ligne de commande pour les chemins de dossiers
#   uncom_files_dir = sys.argv[-4] #location for the original files
#   splitted_files_dir = sys.argv[-3]
#   optimized_files_dir = sys.argv[-2]
#   export_dir = sys.argv[-1]

#   #python .\main.py ./input_data/ ./splitted_data/ ./optimized_data/ ./export_folder/

#   ipr_data_filename = "IPR.csv"
#   landmark_data_filename = 'landmarks.txt'
#   landmarkxls_data_filename = 'landmarks.xls'
#   pathMovementTable = 'Movement table.csv'
#   bolton_analysis_file = 'landmarks_bolton.xls'

#   #output data.json file to be stored in optimized data folder
#   output_json_filename = 'data.json'
#   output_history_filename = 'history.json'

#   generateOptimizedData(
#     uncom_files_dir, 
#     splitted_files_dir, 
#     optimized_files_dir, 
#     export_dir, 
#     ipr_data_filename, 
#     landmark_data_filename, 
#     output_json_filename, 
#     bolton_analysis_file=bolton_analysis_file, 
#     landmarkxls_data_filename=landmarkxls_data_filename, 
#     pathMovementTable=pathMovementTable, 
#     output_history_filename=output_history_filename
#   )


import threading
import sys
import asyncio
from objsplit import generateOptimizedData 

async def run_generateOptimizedData(uncom_files_dir, splitted_files_dir, optimized_files_dir, export_dir):
    ipr_data_filename = "IPR.csv"
    landmark_data_filename = 'landmarks.txt'
    landmarkxls_data_filename = 'landmarks.xls'
    pathMovementTable = 'Movement table.csv'
    bolton_analysis_file = 'landmarks_bolton.xls'

    output_json_filename = 'data.json'
    output_history_filename = 'history.json'

    await generateOptimizedData(
        uncom_files_dir, 
        splitted_files_dir, 
        optimized_files_dir, 
        export_dir, 
        ipr_data_filename, 
        landmark_data_filename, 
        output_json_filename, 
        bolton_analysis_file=bolton_analysis_file, 
        landmarkxls_data_filename=landmarkxls_data_filename, 
        pathMovementTable=pathMovementTable, 
        output_history_filename=output_history_filename
    )

async def main():
    # Arguments de ligne de commande pour les chemins de dossiers
    uncom_files_dir = sys.argv[-4] #location for the original files
    splitted_files_dir = sys.argv[-3]
    optimized_files_dir = sys.argv[-2]
    export_dir = sys.argv[-1]

    # Lancement de la fonction asynchrone
    await run_generateOptimizedData(uncom_files_dir, splitted_files_dir, optimized_files_dir, export_dir)
    print("Async function has finished execution.")

if __name__ == "__main__":
    # Lancement de l'événement boucle d'événement
    asyncio.run(main())

    # # Arguments de ligne de commande pour les chemins de dossiers
    # uncom_files_dir = sys.argv[-4] #location for the original files
    # splitted_files_dir = sys.argv[-3]
    # optimized_files_dir = sys.argv[-2]
    # export_dir = sys.argv[-1]

    # # Créer et démarrer un seul thread
    # thread = threading.Thread(target=run_generateOptimizedData, args=(uncom_files_dir, splitted_files_dir, optimized_files_dir, export_dir))
    # thread.start()

    # # Attendre que le thread soit terminé
    # thread.join()

    # print("Thread has finished execution.")

