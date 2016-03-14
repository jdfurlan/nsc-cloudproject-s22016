from storage_methods import uploadBlob, deleteBlob
from documentdb_methods import createRecord, getRecords, deleteRecord, updateRecord
from verify_oauth import verifyOauth
from static.app_json import *

#uploadImageJSON handles each of the calls necessary to upload an image
#If any step fails, it sends a JSON error response
#First step is verifyOauth using the token and secret handed to this method
#If verified, then attempt to upload a blob given the name, blob and filename
#If uploaded, then create the metadata for the image in documentDB.
def uploadImageJSON(username, blob, filename, token, secret, tags):
    oauth_verify_code = verifyOauth(token, secret)#calls verifyOauth in verify_oauth script
    if oauth_verify_code != 200:#any response other than 200 is a failure, send failure response
        return oauth_error_json
        
    rtnBlobList = uploadBlob(username, blob, filename)#calls uploadBlob in storage_methods script
    if len(rtnBlobList) < 2: #a good response will send a list of length 2, if less than 2 then upload failed
        return upload_image_blob_error_json


    rtnDocumentdbMsg = createRecord(username, filename, tags, rtnBlobList[0], rtnBlobList[1])#calls createRecord in documentdb_methods
    if rtnDocumentdbMsg  == 'error': #if error, metadata creation failed
        return upload_image_db_error_json
        
    return upload_image_success_json

#deleteImageJSON handles each of the calls necessary to upload an image
#If any step fails, it sends a JSON error response
#verifies oauth, calls deleteBlob, then deletes record in documentDB
def deleteImageJSON(blobURL, token, secret):
    oauth_verify_code = verifyOauth(token, secret)
    if oauth_verify_code != 200:#any response other than 200 is a failure, send failure response
        return oauth_error_json
    
    rtnBlobList = deleteBlob(blobURL)#call to delete the blob in storage
    if rtnBlobList == 'error':#if failed, return failure json
        return delete_image_blob_error_json

    rtnDbMsg = deleteRecord(blobURL)#call to delete record in documentDB
    if rtnDbMsg == 'error':#if failed, return failure json
        return delete_image_db_error_json

    return delete_image_success_json
#getImagesJSON checks oauth as usual, then pulls records from documentDB based on input given
def getImagesJSON(timestamp, prev, tags, username, token, secret):
    oauth_verify_code = verifyOauth(token, secret)
    if oauth_verify_code != 200:#any response other than 200 is a failure, send failure response
        return oauth_error_json

    rec_json = getRecords(username, timestamp, prev, tags)#calls getRecords in documentdb_methods
    if rec_json == 'error':
        return get_image_error_json

    rtn_json = {'status': 'success', 'imgs': rec_json}         
    return rtn_json

#updateTagsJSON is used when a user wants to update the tags attached to an already existing record in the DB
def updateTagsJSON(blobURL, tags, token, secret):
    oauth_verify_code = verifyOauth(token, secret)
    if oauth_verify_code != 200:#any response other than 200 is a failure, send failure response
        return oauth_error_json

    rtnDbMsg = updateRecord(blobURL,tags)#calls updateRecord and hands it the new tags to be attached to the document based on URL
    if rtnDbMsg == 'error':
        return update_tags_error_json
    
    return update_tags_success_json

def main():
    pass
    #print(uploadImageJSON('fin', '/Users/rjhunter/Desktop/bridge.jpg', 'Todd','4800385332-ZbrU1XfignI2lA3MjQu7U8KbIkTdYAdj1ArMVFR','BPSs4gwICptsGVZQc9F2EpWcw6ar1gsv4Nlnqvq5PFIdF','love happy hell'))
    #print(deleteImageJSON('https://ad440rjh.blob.core.windows.net/fin/2016-03-12023819187559_Todd','4800385332-ZbrU1XfignI2lA3MjQu7U8KbIkTdYAdj1ArMVFR','BPSs4gwICptsGVZQc9F2EpWcw6ar1gsv4Nlnqvq5PFIdF'))
    #print(getImagesJSON(0,'false',['love'], 'fin','4800385332-ZbrU1XfignI2lA3MjQu7U8KbIkTdYAdj1ArMVFR','BPSs4gwICptsGVZQc9F2EpWcw6ar1gsv4Nlnqvq5PFIdF'))
    #print(updateTagsJSON("https://ad440rjh.blob.core.windows.net/fin/2016-03-12023819187559_Todd", ['fun','luck'],'4800385332-ZbrU1XfignI2lA3MjQu7U8KbIkTdYAdj1ArMVFR','BPSs4gwICptsGVZQc9F2EpWcw6ar1gsv4Nlnqvq5PFIdF'))


# call main
if __name__ == "__main__":
    main()
