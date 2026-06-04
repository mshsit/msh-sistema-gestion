from supabase import create_client

url = "https://unsugrcleytqroxuuhaf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVuc3VncmNsZXl0cXJveHV1aGFmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk5MjkwMDcsImV4cCI6MjA5NTUwNTAwN30.7_P1zqSGX9zffIgYauzjObBjmGnpJmsfjVNOmX_Lmvc"

sb = create_client(url, key)

# Tomar el primer registro
res = sb.table("almacen_prestamos").select("*").limit(1).execute()
print("Registro actual:", res.data)

if res.data:
    primer_id = res.data[0]["id"]
    
    # Intentar modificar varios campos
    payload = {
        "responsable": "PRUEBA MODIFICAR",
        "estado": "Asignado",
        "alerta": "SI"
    }
    
    print(f"\nModificando ID: {primer_id}")
    print(f"Payload: {payload}")
    
    res2 = sb.table("almacen_prestamos").update(payload).eq("id", primer_id).execute()
    print(f"Respuesta: {res2.data}")