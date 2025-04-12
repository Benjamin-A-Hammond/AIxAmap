// static/app.js
document.addEventListener('DOMContentLoaded', function() {
    const chatArea = document.getElementById('chat-area');
    const userInputForm = document.getElementById('user-input-form');
    const userInput = document.getElementById('user-input');
    const mapContainer = document.getElementById('map-container');
    
    // 初始化地图
    const map = new AMap.Map(mapContainer, {
        zoom: 4,
        center: [116.397428, 39.90923] // 中国中心点
    });
    
    // 添加地图控件
    map.plugin(['AMap.ToolBar', 'AMap.Scale'], function() {
        map.addControl(new AMap.ToolBar());
        map.addControl(new AMap.Scale());
    });
    
    // 存储所有标记点
    let markers = [];
    
    // 处理用户输入
    userInputForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;
        
        // 添加用户消息到聊天区域
        addMessage('user', text);
        
        // 清空输入框
        userInput.value = '';
        
        // 添加正在处理的消息
        addMessage('ai', '正在分析您的需求，请稍候...');
        
        try {
            // 发送请求到后端
            const formData = new FormData();
            formData.append('user_input', text);
            
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            // 替换正在处理的消息
            const lastMessage = chatArea.lastElementChild;
            if (lastMessage && lastMessage.classList.contains('ai')) {
                chatArea.removeChild(lastMessage);
            }
            
            // 处理结果
            if (data.locations && data.locations.length > 0) {
                // 清除之前的标记
                clearMarkers();
                
                // 添加新标记
                const bounds = new AMap.Bounds();
                const locationNames = data.locations.map(loc => loc.name).join('、');
                
                addMessage('ai', `已为您在地图上标记了以下地点：${locationNames}`);
                
                // 添加位置标记到地图
                data.locations.forEach(location => {
                    const position = new AMap.LngLat(location.location[0], location.location[1]);
                    bounds.extend(position);
                    
                    const marker = new AMap.Marker({
                        position: position,
                        title: location.name,
                        animation: 'AMAP_ANIMATION_DROP'
                    });
                    
                    // 添加信息窗体
                    const infoWindow = new AMap.InfoWindow({
                        content: `<div><h3>${location.name}</h3></div>`,
                        offset: new AMap.Pixel(0, -30)
                    });
                    
                    marker.on('click', function() {
                        infoWindow.open(map, marker.getPosition());
                    });
                    
                    map.add(marker);
                    markers.push(marker);
                });
                
                // 调整地图视图以包含所有标记
                if (markers.length > 0) {
                    map.setBounds(bounds);
                }
            } else {
                addMessage('ai', '抱歉，我没有找到任何有效的地点。请尝试更具体的地点名称。');
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('ai', '处理您的请求时发生错误，请稍后再试。');
        }
    });
    
    // 添加消息到聊天区域
    function addMessage(type, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        messageDiv.textContent = text;
        chatArea.appendChild(messageDiv);
        
        // 滚动到底部
        chatArea.scrollTop = chatArea.scrollHeight;
    }
    
    // 清除所有标记
    function clearMarkers() {
        if (markers.length > 0) {
            map.remove(markers);
            markers = [];
        }
    }
});