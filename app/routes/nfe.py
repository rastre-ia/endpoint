from fastapi import APIRouter, HTTPException

router = APIRouter()

CHAVE_ACESSO_FIXA = "42231026093223000134550010000145361344775104"
NFE_RESPONSE = {
  "nfeProc": {
    "protNFe": {
      "infProt": {
        "nProt": 353170008206589,
        "digVal": "2dbfjHUlSwifyusOJICxaHW2rKk=",
        "dhRecbto": "2017-06-05T08:31:06-03:00",
        "chNFe": "42231026093223000134550010000145361344775104",
        "xMotivo": "Autorizado o uso da NF-e",
        "cStat": 100
      }
    },
    "NFe": {
      "infNFe": {
        "infAdic": {
          "infCpl": "N/PED.: 051542;VL. APRX. TRIB.(FONTE IBPT): ****254.19  **34.12 %"
        },
        "det": [
          {
            "nItem": 1,
            "prod": {
              "cEAN": "",
              "cProd": 346,
              "qCom": 5,
              "cEANTrib": "",
              "vUnTrib": 149,
              "qTrib": 5,
              "vProd": 745,
              "xProd": "SULFITE A4 75GR BOREAL (5000FLS)",
              "vUnCom": 149,
              "indTot": 1,
              "uTrib": "RS",
              "NCM": 48025610,
              "uCom": "RS",
              "CFOP": 5102,
              "CEST": 9999999
            },
            "imposto": {
              "vTotTrib": 254.19,
              "ICMS": {
                "ICMS00": {
                  "modBC": 0,
                  "orig": 0,
                  "CST": "00",
                  "vBC": 745,
                  "vICMS": 134.1,
                  "pICMS": 18
                }
              },
              "COFINS": {
                "COFINSAliq": {
                  "vCOFINS": 22.35,
                  "CST": "01",
                  "vBC": 745,
                  "pCOFINS": 3
                }
              },
              "PIS": {
                "PISAliq": {
                  "vPIS": 4.84,
                  "CST": "01",
                  "vBC": 745,
                  "pPIS": 0.65
                }
              }
            }
          }
        ],
        "total": {
          "ICMSTot": {
            "vCOFINS": 22.35,
            "vBCST": 0,
            "vICMSDeson": 0,
            "vProd": 745,
            "vSeg": 0,
            "vNF": 745,
            "vTotTrib": 254.19,
            "vPIS": 4.84,
            "vBC": 745,
            "vST": 0,
            "vICMS": 134.1,
            "vII": 0,
            "vDesc": 0,
            "vOutro": 0,
            "vIPI": 0,
            "vFrete": 0
          }
        },
        "cobr": {
          "dup": [
            {
              "dVenc": "2017-07-05",
              "nDup": "015430/A",
              "vDup": 372.5
            },
            {
              "dVenc": "2017-07-20",
              "nDup": "015430/B",
              "vDup": 372.5
            }
          ]
        },
        "Id": "NFe42231026093223000134550010000145361344775104",
        "ide": {
          "tpNF": 1,
          "mod": 55,
          "indPres": 0,
          "tpImp": 1,
          "nNF": 15430,
          "cMunFG": 3550308,
          "procEmi": 0,
          "finNFe": 1,
          "dhEmi": "2017-06-05T08:31:06-03:00",
          "tpAmb": 1,
          "indFinal": 1,
          "idDest": 1,
          "tpEmis": 1,
          "cDV": 9,
          "cUF": 35,
          "serie": 0,
          "natOp": "VENDA",
          "cNF": "00077156",
          "verProc": "3.10.31",
          "indPag": 1
        },
        "emit": {
          "xNome": "COMERCIO DE TESTE LTDA EPP",
          "CRT": 3,
          "xFant": "comerciodeteste@comerciodeteste.com.br",
          "CNPJ": "56776378000136",
          "enderEmit": {
            "fone": 995551234,
            "UF": "SP",
            "xPais": "BRASIL",
            "cPais": 1058,
            "xLgr": "AV FICTICIA",
            "xMun": "SAO PAULO",
            "nro": 80,
            "cMun": 3550308,
            "xBairro": "VILA FICTICIA",
            "CEP": "00012345"
          },
          "IE": 123456789123
        },
        "dest": {
          "xNome": "JOÃO DA SILVA",
          "CPF": 11111111111,
          "enderDest": {
            "fone": 995551234,
            "UF": "SP",
            "xPais": "BRASIL",
            "cPais": 1058,
            "xLgr": "AV FICTICIA, 1579",
            "xMun": "SAO PAULO",
            "nro": ".",
            "cMun": 3550308,
            "xBairro": "SANTO AMARO FICTICIO",
            "CEP": "00033200"
          },
          "indIEDest": 9
        },
        "transp": {
          "modFrete": 0,
          "vol": {
            "pesoL": 116.944,
            "esp": "RESMAS",
            "qVol": 5,
            "pesoB": 116.944
          },
          "transporta": {
            "xNome": "TRANSPORTADORA FICTICIA"
          }
        }
      }
    },
    "versao": 3.1
  }
}


@router.post("/")
async def get_nfe(data: dict):
    chave_acesso = data.get("chave_acesso")
    if chave_acesso == CHAVE_ACESSO_FIXA:
        return NFE_RESPONSE
    raise HTTPException(status_code=404, detail="NF-e não encontrada para a chave de acesso fornecida.")
