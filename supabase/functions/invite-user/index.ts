// Supabase Edge Function: invite-user
//
// Lets the creator invite a new user by email. The service-role key
// stays on the server — never in the browser. Caller must be signed
// in AND match CREATOR_EMAIL.
//
// Deploy:
//   supabase functions deploy invite-user
//
// Set the service role secret (one-time):
//   supabase secrets set SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
//
// (SUPABASE_URL and SUPABASE_ANON_KEY are auto-injected by Supabase.)

import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const CREATOR_EMAIL = 'ahmed.mouatamid@z.systems'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers':
    'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' },
  })
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }
  if (req.method !== 'POST') {
    return json({ error: 'POST only' }, 405)
  }

  try {
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) return json({ error: 'Missing Authorization header' }, 401)

    const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
    const SUPABASE_ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY')!
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!

    // Verify the caller is the creator using their JWT.
    const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      global: { headers: { Authorization: authHeader } },
    })
    const { data: userData, error: userErr } = await userClient.auth.getUser()
    if (userErr || !userData.user) {
      return json({ error: 'Not signed in' }, 401)
    }
    const callerEmail = (userData.user.email || '').toLowerCase()
    if (callerEmail !== CREATOR_EMAIL.toLowerCase()) {
      return json({ error: 'Forbidden — only the creator can invite' }, 403)
    }

    // Parse body.
    const body = await req.json().catch(() => ({}))
    const email = (body.email || '').trim()
    const seller = (body.seller || '').trim()  // optional: marks user as a seller
    if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      return json({ error: 'Valid email required' }, 400)
    }

    // Service-role admin client — bypasses RLS, can invite users.
    const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    // Stash the seller name in user_metadata so the frontend can read it
    // back via sbUser.user_metadata.seller.
    const { data, error } = await admin.auth.admin.inviteUserByEmail(email, {
      data: seller ? { seller, role: 'seller' } : undefined,
    })
    if (error) {
      return json({ error: error.message }, 400)
    }

    return json({ ok: true, userId: data.user?.id, email: data.user?.email, seller: seller || null })
  } catch (e) {
    return json({ error: e instanceof Error ? e.message : String(e) }, 500)
  }
})
