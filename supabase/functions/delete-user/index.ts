// Supabase Edge Function: delete-user
//
// Lets the creator delete a user by email. Service-role only — never exposed
// to the browser. Caller must be the creator (verified via JWT).
//
// Deploy:
//   supabase functions deploy delete-user

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

    // Verify the caller is the creator.
    const userClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      global: { headers: { Authorization: authHeader } },
    })
    const { data: userData, error: userErr } = await userClient.auth.getUser()
    if (userErr || !userData.user) return json({ error: 'Not signed in' }, 401)
    const callerEmail = (userData.user.email || '').toLowerCase()
    if (callerEmail !== CREATOR_EMAIL.toLowerCase()) {
      return json({ error: 'Forbidden — only the creator can delete users' }, 403)
    }

    const body = await req.json().catch(() => ({}))
    const targetEmail = (body.email || '').trim().toLowerCase()
    if (!targetEmail) return json({ error: 'Email required' }, 400)
    if (targetEmail === CREATOR_EMAIL.toLowerCase()) {
      return json({ error: 'Cannot delete the creator account' }, 400)
    }

    // Admin client (bypasses RLS).
    const admin = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

    // Look up the user by email (paginate the list — small team).
    const { data: list, error: listErr } = await admin.auth.admin.listUsers({
      page: 1, perPage: 1000,
    })
    if (listErr) return json({ error: listErr.message }, 500)
    const target = (list.users || []).find(
      u => (u.email || '').toLowerCase() === targetEmail
    )
    if (!target) return json({ error: 'User not found' }, 404)

    const { error: delErr } = await admin.auth.admin.deleteUser(target.id)
    if (delErr) return json({ error: delErr.message }, 500)

    return json({ ok: true, deletedId: target.id, email: targetEmail })
  } catch (e) {
    return json({ error: e instanceof Error ? e.message : String(e) }, 500)
  }
})
