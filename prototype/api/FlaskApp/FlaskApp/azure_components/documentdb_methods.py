import pydocumentdb.document_client as document_client
import verify_oauth
import datetime
from datetime import timedelta
from static.app_keys import db_client, db_client_key, db_name, db_collection
	

#createRecord is how metadata is created for an image once it has passed
#the two initial steps of verifying oauth and uploading to blob storage
#Takes the username, filename, tags, time and url to be stored in DB for the image
def createRecord(user, originalFilename, tags, time, url):
    try:
    	#epoc is used to generate a datetime object from time specified.
        epoc = datetime.datetime(2016, 2, 23, 3, 0, 00, 000000);
        #val is an integer (miliseconds) from the epoc, which then creates a completely unique "ID" for the image
        #this is used also to ensure that image ID's are always ascending based on time created.
        #documentDB doesn't allow for datetime comparisons which is why we needed a number that was constantly growing larger
        val = (time - epoc).total_seconds()*1000000;
        #connection to client using the pydocumentdb SDK       
        client = document_client.DocumentClient(db_client, {'masterKey': db_client_key});
        #connect to the database
        db = next((data for data in client.ReadDatabases() if data['id'] == db_name));
        #connect to the collection
        coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == db_collection));
        #create document. Tags is an array, as passed.
        document = client.CreateDocument(coll['_self'],
                        {   "user_id": user,
                                "file_name": originalFilename,
                                "photo_url": url,
                                "photo_id": val,
                                "tags": tags
                        });

        return "success"
        
    except Exception:
        return "error"
#getRecords pulls URLs from the database based on user input
def getRecords(user, lastID, prev, tags):

    try:
    	#if user chose "next" pull records ascending
        dir = ">"
        order = "ASC"
	#if use chose "previous" pull records descending
        if prev != 'false':
            dir = "<"
            order = "DESC"
        #connections to database
        client = document_client.DocumentClient(db_client, {'masterKey': db_client_key})
        db = next((data for data in client.ReadDatabases() if data['id'] == db_name))
        coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == db_collection))
	#queryString attempts to pull the top 20 URLs based on direction specified
	#if the user chose "prev" then it must check for 20 IDs greater than the smallest value
	#on the previous page, else pull 20 IDs greater then the largest value on the page.
	#Initial value will be 0 if first page
        queryString = 'SELECT TOP 20 ' + db_collection + '.photo_id, ' + \
                        db_collection +'.file_name, ' + db_collection + '.photo_url, ' + db_collection + \
                        '.tags FROM '+ db_collection + ' WHERE '+ db_collection + '.user_id = "' \
                        + user + '" AND ' + db_collection + '.photo_id ' + dir + ' ' + str(lastID)
	#if tags are given in the search, append them into the query and limit results based on tags
        if len(tags) > 0:
            for tag in tags:
                queryString += ' AND ARRAY_CONTAINS(' + db_collection + '.tags ,"' + tag + '")'
	#order by the ID's which are timestamps(miliseconds) and always ascending
        queryString += ' ORDER BY '+ db_collection +'.photo_id '+ order
	#add query result into list
        itterResult =  client.QueryDocuments(coll['_self'], queryString)
        rtn_list = list(itterResult)
	#if it was a "previous" search, reverse order since they would display values largest to smallest otherwise
        if prev != 'false':
            rtn_list_new = sorted(rtn_list, reverse=True)
            return sorted(rtn_list_new)
        
        return rtn_list

    except Exception:
        return "error"
#deleteRecord just takes the URL of the image to be deleted
def deleteRecord(blobURL):
    try:
    	#connections to the DB
        client = document_client.DocumentClient(db_client, {'masterKey': db_client_key})
        db = next((data for data in client.ReadDatabases() if data['id'] == db_name))
        coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == db_collection))
        # Read documents and take first since id should not be duplicated.
        doc = next((doc for doc in client.ReadDocuments(coll['_self']) if doc['photo_url'] == blobURL))
        #delete the record
        client.DeleteDocument(doc['_self'])
        return 'success'

    except Exception:
        return 'error'

#updateRecord receives the blobURL to locate the document
#and tags which are to be used to replace the current tags in the document
def updateRecord(blobURL, tags):

    try:
        #these function calls are used to locate the db client, database, collection, then the actual document
        #based off the URL provided
        client = document_client.DocumentClient(db_client, {'masterKey': db_client_key})
        db = next((data for data in client.ReadDatabases() if data['id'] == db_name))
        coll = next((coll for coll in client.ReadCollections(db['_self']) if coll['id'] == db_collection))        
        doc = next((doc for doc in client.ReadDocuments(coll['_self']) if doc['photo_url'] == blobURL))

        #changes the tags field to the new one provided by the user
        doc['tags'] = tags 
        #replaces the current document with the new document, with updated tags
        replaced_document = client.ReplaceDocument(doc['_self'], doc)
        return "success"
    
    except Exception:
        return "error"

def main():
    pass
    #time = datetime.datetime.utcnow()
    #print(makeMetadata('tom','filename2',['fun','tom'], time, "www.happy.com"))
    #fun = getRecords('fin',1214137258909, 'true', [])
    #print(fun)
    #fun = deleteRecord('www.test.com')
    #print(fun)
    #tags = ['mom', 'dad', 'trees', 'cat']
    #print(updateRecord('https://ad440rjh.blob.core.windows.net/fin/2016-03-08041411903453_Todd', tags))    
    
if __name__ == "__main__":
    main()
