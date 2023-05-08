class MyUploadAdapter {
    constructor( loader, csrf_token ) {
        // The file loader instance to use during the upload.
        // 업로드 하는 동안 사용할 업로드 인스턴스
        this.loader = loader;

        this.url = '/admin/notice/image'
        this.csrf_token = csrf_token
        }

        // Starts the upload process.
        // 업로드 과정 시작
        upload() {
            return this.loader.file
                .then( file => new Promise( ( resolve, reject ) => {
                    this._initRequest();
                    this._initListeners( resolve, reject, file );
                    this._sendRequest( file );
                } ) )
        }

        // Aborts the upload process.
        // 업로드 과정을 중지
        abort() {
            if ( this.xhr ) {
                this.xhr.abort();
            }
        }

        // Initializes the XMLHttpRequest object using the URL passed to the constructor.
        // 생성자에 전달된 URL을 가지고 XMLHttpRequest객체를 초기화
        _initRequest() {
            const xhr = this.xhr = new XMLHttpRequest();

            // Note that your request may look different. It is up to you and your editor
            // 나와 나의 에디터에 따라서 다르게 보이는 부분이다.
            xhr.open( 'POST', this.url, true);
            xhr.responseType = 'json';
        }

        // Initializes XMLHttpRequest listeners.
        // XMLHttpRequest리스너를 초기화
        _initListeners( resolve, reject, file ) {
            const xhr = this.xhr;
            const loader = this.loader;
            const genericErrorText = `Could not upload file: ${ file.name }.`;

            xhr.addEventListener( 'error', () => reject( genericErrorText ) );
            xhr.addEventListener( 'abort', () => reject() );
            xhr.addEventListener( 'load', () => {
                const response = xhr.response;

                // 이 부분에서 response가 없거나 error을 가지고 오게 된다면 reject()를 실행한다.
                // 업로드에 실패한 경우에는 반드시 reject()를 호출해야만 한다.
                if ( !response || response.error ) {
                    return reject( response && response.error ? response.error.message : genericErrorText );
                }

                // 만약 업로드에 성공한다면 적어도 디폴트 url이 담겨있는 객체를 이용해서 업로드 프로미스를 해결한다
                // 그리고 이 디폴트 url은 서버상의 이미지를 가리킨다.
                // 이 url들은 내용에서 이미지를 출력하는데 사용될 것이다.
                // Learn more in the UploadAdapter#upload documentation.
                resolve( {
                    default: response.url
                } );
            } );
        }

        // 데이터를 준비하고 요청을 보낸다.
        _sendRequest( file ) {
            // form data를 준비한다.
            const data = new FormData();

            // upload라는 이름으로 file을 담는다.
            data.append( 'upload', file);

            // 중요한 노트: 이 부분은 보안에 관련된 메커니즘을 포함시키는 부분이다.
            // 사용자 증명, CSRF 보안등. 예를 들어서 XMLHttpRequest.setRequestHeader()
            // 을 이용해서 CSRF Token을 삽입할 수 있다.
            this.xhr.setRequestHeader('X-CSRFToken', this.csrf_token);


            // 요청을 보낸다.
            this.xhr.send( data );
        }
    }
/*
function MyCustomUploadAdapterPlugin( editor ) {
    editor.plugins.get( 'FileRepository' ).createUploadAdapter = ( loader ) => {
        // 백엔드에서 업로드 할 url을 여기서 구성한다.
        return new MyUploadAdapter( loader );
    }
}*/