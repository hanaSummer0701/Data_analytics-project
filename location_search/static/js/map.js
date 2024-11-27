// 불용어 리스트
const stopWords = ['주차장', '남원윤씨', '사거리', '장난감', '역점', '역지점', '예정','부동산', '노래', '본점', '은행'];

// Kakao 지도 로드
kakao.maps.load(function() {
    // Kakao 지도 객체 생성
    var mapContainer = document.getElementById('map'), 
        mapOption = {
            center: new kakao.maps.LatLng(37.486320, 126.898530), 
            level: 4 
        };
    var map = new kakao.maps.Map(mapContainer, mapOption);

    // 주소-좌표 변환 객체 생성 (전역 변수로 설정)
    window.geocoder = new kakao.maps.services.Geocoder();

    // 인포윈도우를 하나만 관리하도록 설정
    var infowindow = new kakao.maps.InfoWindow({zIndex: 1});

    // 여러 주소 처리
    locations.forEach(function(item) {
        // 불용어가 포함된 주소인지 확인
        if (!containsStopWords(item.address)) {
            // 주소로 좌표 변환
            geocoder.addressSearch(item.address, function(result, status) {
                if (status === kakao.maps.services.Status.OK) {
                    var coords = new kakao.maps.LatLng(result[0].y, result[0].x);

                    // 마커 추가
                    var marker = new kakao.maps.Marker({
                        map: map,
                        position: coords
                    });

                    // 마커 클릭 시 인포윈도우 표시
                    kakao.maps.event.addListener(marker, 'click', function() {
                        // 기존에 열린 인포윈도우 닫기
                        infowindow.close();

                        // 클릭한 마커의 정보를 표시할 새로운 인포윈도우 내용
                        var content = '<div style="width:300px;text-align:center;padding:6px 0;">' +
                                    '<strong>' + item.title + '</strong><br>' +
                                    'address : ' + item.address + '<br>' +
                                    'Point : ' + item.point + '<br>' +
                                    // 'URL : ' + item.url + '<br>'+
                                    // '<a href="' + item.url + '" target="_blank">homepage</a>' +
                                    '</div>';

                        // 새로운 인포윈도우를 열기
                        infowindow.setContent(content);
                        infowindow.open(map, marker);

                        // 표 업데이트
                        updateInfoTableWithSingleMarker(item);
                        
                        // 가까운 역 찾기
                        findNearestStation(coords, item);
                    });

                    // 지도의 중심을 해당 주소로 이동
                    map.setCenter(coords);
                }
            });
        } else {
            console.log(`주소 "${item.address}"는 불용어가 포함되어 있어 검색하지 않습니다.`);
        }
    });
});

// 불용어가 포함되어 있는지 확인하는 함수 (단일 정의)
function containsStopWords(address) {
    return stopWords.some(stopWord => address.includes(stopWord));
}

// 가장 가까운 역 찾기
function findNearestStation(coords, item) {
    var places = new kakao.maps.services.Places();
    
    // "역"으로 검색
    places.keywordSearch('역', function(data, status, pagination) {
        if (status === kakao.maps.services.Status.OK && data.length > 0) {
            let nearestStation = null;

            // 불용어가 포함되지 않은 역 찾기
            for (let station of data) {
                if (!containsStopWords(station.place_name)) {
                    nearestStation = station;
                    break; // 불용어가 없는 첫 번째 역을 찾으면 루프 종료
                }
            }

            // 가장 가까운 역이 발견된 경우
            if (nearestStation) {
                var stationCoords = new kakao.maps.LatLng(nearestStation.y, nearestStation.x);
                
                // 거리 계산 (미터 단위)
                if (coords && stationCoords) {
                    var distance = getDistance(coords, stationCoords); // 거리 계산 함수 호출
                    
                    // 정보 표 업데이트
                    updateInfoTable(item, nearestStation.place_name, distance);
                }
            } else {
                // 불용어가 포함된 역이 없을 경우
                updateInfoTable(item, '역 없음', '정보 없음');
            }
        } else {
            console.log('역 검색 실패: ' + status);
            // 역이 발견되지 않았을 경우
            updateInfoTable(item, '역 없음', '2km 이상');
        }
    }, { location: coords, radius: 2000 }); // 검색 반경 1km
}

// 거리 계산 함수
function getDistance(coords1, coords2) {
    var lat1 = coords1.getLat();
    var lng1 = coords1.getLng();
    var lat2 = coords2.getLat();
    var lng2 = coords2.getLng();

    // Haversine formula (지구의 곡률을 고려한 거리 계산)
    var R = 6371e3; // 지구의 반지름 (미터)
    var φ1 = lat1 * Math.PI/180; // 위도
    var φ2 = lat2 * Math.PI/180;
    var Δφ = (lat2-lat1) * Math.PI/180;
    var Δλ = (lng2-lng1) * Math.PI/180;

    var a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return Math.round(R * c); // 거리 (미터 단위)
}

// 마커 클릭 시 단일 마커 정보로 표 업데이트
function updateInfoTableWithSingleMarker(item) {
    const tableBody = document.getElementById('infoTableBody');

    // 기존 행을 제거하지 않고 새로운 정보를 추가
    const existingRows = tableBody.getElementsByTagName('tr');
    for (let row of existingRows) {
        if (row.cells[0].innerText === item.title && row.cells[1].innerText === item.address) {
            // 이미 존재하는 경우 행을 업데이트하고 종료
            row.cells[6].innerText = '정보 없음'; // 가까운 역 이름
            row.cells[7].innerText = '정보 없음'; // 거리
            return;
        }
    }
    // 이전 표 내용 초기화
    tableBody.innerHTML = '';
    // 새 행 생성
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${item.title}</td>
        <td>${item.address}</td>
        <td>${item.point}</td>
        <td><a href="${item.url}" target="_blank"></td>
        <td>${item.region}</td>
        <td>${item.condition.replace(/<br>/g, '<br />')}</td>
        <td>${item.contact}</td>
        <td>${'정보 없음'}</td> <!-- 가까운 역 이름 -->
        <td>${'정보 없음'}</td> <!-- 거리 -->
    `;
    tableBody.appendChild(row);
}


// 지역 선택 박스의 이벤트 리스너 추가 
document.addEventListener("DOMContentLoaded", function() {
    // 지역 선택 박스의 이벤트 리스너 추가
    document.getElementById('regionSelect').addEventListener('change', function() {
        const selectedRegion = this.value; // 선택한 지역
        const filteredLocations = locations.filter(item => 
            item.region === selectedRegion || selectedRegion === ""); // 지역 필터링

        // 이전 테이블 내용 초기화
        const tableBody = document.getElementById('infoTableBody');
        tableBody.innerHTML = '';

        filteredLocations.forEach(function(item) {
            // 주소로 좌표 변환
            geocoder.addressSearch(item.address, function(result, status) {
                if (status === kakao.maps.services.Status.OK) {
                    var coords = new kakao.maps.LatLng(result[0].y, result[0].x);
                    findNearestStation(coords, item); // 각 마커에 대해 가까운 역 계산
                }
            });
        });
    });
});

// 정보 표 업데이트 함수
function updateInfoTable(item, nearestStationName, distance) {
    const tableBody = document.getElementById('infoTableBody');
    
    // 기존 행을 찾아 업데이트
    const existingRows = tableBody.getElementsByTagName('tr');
    for (let row of existingRows) {
        if (row.cells[0].innerText === item.title && row.cells[1].innerText === item.address) {
            row.cells[7].innerText = nearestStationName; // 가까운 역 이름 업데이트
            row.cells[8].innerText = distance !== '2km 이상' ? distance + 'm' : distance; // 거리 업데이트
            row.setAttribute('data-url', item.url); // URL 데이터 업데이트
            return;
        }
    }

    // 새로운 행 추가
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${item.title}</td>
        <td>${item.address}</td>
        <td>${item.point}</td>
        <td>${item.url}</td>
        <td>${item.region}</td>
        <td>${item.condition.replace(/<br>/g, '<br />')}</td>
        <td>${item.contact}</td>
        <td>${nearestStationName}</td> <!-- 가까운 역 이름 -->
        <td>${distance !== '2km 이상' ? distance + 'm' : distance}</td> <!-- 거리 -->
    `;
    tableBody.appendChild(row);
}