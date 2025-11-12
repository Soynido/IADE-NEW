// Test rapide de l'API Redis Upstash
const REDIS_URL = "https://full-crab-26762.upstash.io";
const REDIS_TOKEN = "AWiKAAIncDJiNWZhOWRlZTkzODA0YTk1YTE2NGJmNWI1Zjg0YWU2Y3AyMjY3NjI";

async function testRedis() {
  try {
    console.log('🔄 Test connexion Redis Upstash...');
    console.log('URL:', REDIS_URL);
    
    const testPayload = {
      questionId: 'test_' + Date.now(),
      score: 3,
      timestamp: new Date().toISOString()
    };
    
    console.log('📤 Envoi payload:', testPayload);
    
    const response = await fetch(`${REDIS_URL}/lpush/feedback:test_connection`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${REDIS_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testPayload)
    });
    
    console.log('📊 Status:', response.status);
    const data = await response.json();
    console.log('📦 Response:', data);
    
    if (response.ok) {
      console.log('✅ Redis fonctionne !');
    } else {
      console.log('❌ Erreur Redis:', response.status, data);
    }
  } catch (error) {
    console.log('❌ Exception:', error.message);
  }
}

testRedis();
