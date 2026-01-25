INSERT INTO usuarios (id, nome, email, whatsapp, data_criacao, data_ultima_edicao, senha, nivel_acesso)
VALUES (
    'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
    'Admin Principal',
    'admin@admin.com',
    '62999999999',
    CURRENT_TIMESTAMP,
    CURRENT_DATE,
    '$2a$12$rvgX1ZbqhzUyO0X99HroXe/TVWkZ4TnYvjaqiyZGvDCAOSFiADGhy',
    'ADMIN'
);

INSERT INTO usuarios (id, nome, email, whatsapp, data_criacao, data_ultima_edicao, senha, nivel_acesso)
VALUES (
    'b1eebc99-1c0b-4ef8-bb6d-7bb9bd380a22',
    'Cliente Teste',
    'cliente@cliente.com',
    '62888888888',
    CURRENT_TIMESTAMP,
    CURRENT_DATE,
    '$2a$12$rvgX1ZbqhzUyO0X99HroXe/TVWkZ4TnYvjaqiyZGvDCAOSFiADGhy',
    'CLIENTE'
);

INSERT INTO canais (data_inclusao,id,nome_canal) VALUES
	 ('2025-11-14','272d6a2d-e0d1-4fa9-abab-055131c2a4cc','Whatsapp'),
	 ('2025-11-14','ed3f001d-655e-428a-9c9f-566e9d4f1203','Email');

INSERT INTO public.cidades (id,nome) VALUES
	 ('38732ef2-b776-483a-b04f-b4b634db446f','Abadia de Goiás'),
	 ('55fc8533-03eb-4180-8e9f-b2c9b2849689','Abadiânia'),
	 ('39b0899b-3807-46a1-9031-d4531cbb0e66','Acreúna'),
	 ('768f1fd6-0f59-429d-b06b-da3897d70470','Adelândia'),
	 ('d39aa33c-8f23-4da3-8c53-b3197297efe5','Água Fria de Goiás'),
	 ('46f2b61f-d644-4eff-abf4-8102357eb528','Água Limpa'),
	 ('b26e3338-27d3-41fe-b56a-32b865eecfd9','Águas Lindas de Goiás'),
	 ('a0b8ed09-db82-40b4-8dc5-6efd086dcb53','Alexânia'),
	 ('139494e5-ffad-4271-8633-998e0b2bcad3','Aloândia'),
	 ('f5be9fd0-75ec-4c67-a04a-967b9200a7ec','Alto Horizonte');
INSERT INTO public.cidades (id,nome) VALUES
	 ('8ce5b84f-25ce-40d2-a7d1-65a074ddc7cb','Alto Paraíso de Goiás'),
	 ('979e6488-3be9-4a21-ab3a-3f8273079d2d','Alvorada do Norte'),
	 ('2737dc42-8188-4163-bbdf-bacfb0ebe95c','Amaralina'),
	 ('3cfae349-2e54-405d-8571-3fc40d1e0b7f','Americano do Brasil'),
	 ('d08f0823-2956-4e46-9fde-38c82e69b64b','Amorinópolis'),
	 ('10f3b6f1-6072-4e4e-8661-17709b095ce5','Anápolis'),
	 ('46fffbf1-4866-46a5-b556-20ed49160faa','Anhanguera'),
	 ('abe8da89-6dbb-4bc5-acf4-adfa2f62c28e','Anicuns'),
	 ('a0460e29-76dd-4348-b006-44e875cdaf11','Aparecida de Goiânia'),
	 ('b1edb2ad-bfb9-498a-8d26-4f50b4d90c6b','Aparecida do Rio Doce');
INSERT INTO public.cidades (id,nome) VALUES
	 ('0b7ebfc6-05fe-438c-8ec0-322a00ee02d8','Apore'),
	 ('2c06fb5e-d797-43f7-ac67-dc3bffa8cdb0','Araçu'),
	 ('f6a88c00-b4ec-408d-b074-b51a5a6f1e35','Aragarças'),
	 ('cf53e8a7-2aea-4cb8-90b8-86cbdad9e1dc','Aragoiânia'),
	 ('e30ff4c4-996f-40b6-883e-67ba91f94f36','Araguapaz'),
	 ('ff95138c-270c-4562-92bf-6eae4605f26b','Arenópolis'),
	 ('28b22242-f25c-4c64-bb48-519b11a147ff','Aruanã'),
	 ('f13ba0f5-d381-41da-a383-3737d7b90884','Aurilândia'),
	 ('263967f0-ec2a-4c3a-9492-a073f889f724','Avelinópolis'),
	 ('efe3494b-3ad6-4cbc-b5f1-28fc1cde7f27','Baliza');
INSERT INTO public.cidades (id,nome) VALUES
	 ('3043d02d-638e-456f-a51e-ad0791def1f5','Barro Alto'),
	 ('2e18353d-c6d2-442c-83fc-68f4fed788ff','Bela Vista de Goiás'),
	 ('bf3b365a-fa28-4ab9-b29b-e8a04db565c7','Bom Jardim de Goiás'),
	 ('4903c394-6e24-44e8-9098-336a092b7a38','Bom Jesus de Goiás'),
	 ('49acaf19-58d1-4058-8158-e43d484a5bed','Bonfinópolis'),
	 ('498f1b14-3f2a-47ea-9f15-05dd8d252cb4','Bonópolis'),
	 ('089d7170-443a-487f-94a7-d9c863c2815a','Brazabrantes'),
	 ('e5d0e4e2-9c2d-49f9-b88f-c6163d6dcf8b','Britânia'),
	 ('7de6d9d6-b241-4570-bdda-33f54603b582','Buriti Alegre'),
	 ('606d11a0-e20b-463c-aefd-4f868af8efd2','Buriti de Goiás');
INSERT INTO public.cidades (id,nome) VALUES
	 ('72ca348f-9adc-4beb-9352-5c7fc049c552','Buritinópolis'),
	 ('2252bfbe-ec20-4e46-9922-c0be593785df','Cabeceiras'),
	 ('9a6cb886-ae7c-400e-bd1b-8c0f4a9f3525','Cachoeira Alta'),
	 ('22d06dc3-6a3b-48a5-8f71-d8eb5139cc72','Cachoeira de Goiás'),
	 ('27e5f3d0-45e8-4afb-b350-f90087733292','Cachoeira Dourada'),
	 ('0279b29f-9bbd-4616-a16f-dd571671f6b9','Caçu'),
	 ('3a9ecd3c-296b-440f-9dfa-981059bee772','Caiapônia'),
	 ('0c51fd92-adcd-4831-aee4-61f085ad161e','Caldas Novas'),
	 ('322de618-e4c2-495c-bdc6-121c11898326','Caldazinha'),
	 ('61b23789-3c3f-4703-b40e-50832925fd68','Campestre de Goiás');
INSERT INTO public.cidades (id,nome) VALUES
	 ('13586a75-5c96-4d63-b69b-6bddf9757dde','Campinaçu'),
	 ('3a2535e5-9f18-41a4-9080-e248b1015498','Campinorte'),
	 ('04e48421-dc9c-4401-9b29-8e083ba01f5c','Campo Alegre de Goiás'),
	 ('0fda8ece-f84f-47cf-affe-471159a08c88','Campo Limpo de Goiás'),
	 ('c2965348-17ed-4a1b-86f3-b2c99275f9d6','Campos Belos'),
	 ('d4acaa41-3302-42ee-9cd6-48d540f32c8e','Campos Verdes'),
	 ('4021319f-5189-4725-8e04-9ed425fd7325','Carmo do Rio Verde'),
	 ('3fbc7c48-1d19-4027-be4f-7e3bb96247e6','Castelândia'),
	 ('3964c7bc-d1d5-44a9-a56a-5305caa2cee5','Catalão'),
	 ('0c5805c6-a30b-47b4-9d5a-3f191227bb67','Caturaí');
INSERT INTO public.cidades (id,nome) VALUES
	 ('93b3faba-f8b6-4e48-93d7-4c3fba88e097','Cavalcante'),
	 ('3b18ef69-e37d-47c3-a862-1cd84a3cde09','Ceres'),
	 ('1dd7c3fc-f6f6-48f4-a46e-09fdbe6670c0','Cezarina'),
	 ('f2aedc96-2011-4af9-a768-d10a7489bbda','Chapadão do Céu'),
	 ('a21f7b81-42ae-4ea1-b09d-dd56c38bba88','Cidade Ocidental'),
	 ('b2570f0a-ba84-46c2-94be-3ffe8702e8bd','Cocalzinho de Goiás'),
	 ('360d005f-92d9-480a-ab98-14c854a1773c','Colinas do Sul'),
	 ('e02e1eb7-44db-4dc0-96e9-626b8c2df230','Córrego do Ouro'),
	 ('471db575-a207-4a0c-9770-cbfe8d65a55b','Corumbá de Goiás'),
	 ('700498e4-6a9c-4949-8d80-8a41a65294ab','Corumbaíba');
INSERT INTO public.cidades (id,nome) VALUES
	 ('0f9a1d33-af42-457c-8b65-838b442921bc','Cristalina'),
	 ('0ef0f885-769e-42f6-8d32-80a02a9575a7','Cristianópolis'),
	 ('e19a2f32-150c-40ab-a678-dc3455c9ae78','Crixás'),
	 ('e4c7c954-6811-49e7-b1d3-03cb38d7a0fa','Cromínia'),
	 ('276337d1-baa2-4f6d-bd55-e1d331a9b3e3','Cumari'),
	 ('bff74849-ccad-4959-b3f3-81b70b09b961','Damianópolis'),
	 ('ca61da4c-cc9a-46b0-af18-8c2e9e35647d','Damolândia'),
	 ('64b3018f-e195-4db8-b409-34da5f1b50c9','Davinópolis'),
	 ('d02b37d6-e33b-4021-82e4-4bd86f977990','Diorama'),
	 ('fac194ad-00f0-470e-a735-d361d5b57015','Divinópolis de Goiás');
INSERT INTO public.cidades (id,nome) VALUES
	 ('fdb8dd1c-8c08-45cf-a515-ecb502636f61','Doverlândia'),
	 ('24bcf266-33c7-4872-b74c-98587314f0f1','Edealina'),
	 ('65f009c2-3f5b-4428-a46b-eda8f87544b7','Edéia'),
	 ('9d8d1280-06e6-4749-af8b-d5d9ce92eb4f','Estrela do Norte'),
	 ('dfe06f11-2155-4c13-9415-7ed3d3ed79b8','Faina'),
	 ('daea27c4-dbba-4b4e-a1c4-0c9a8b60f771','Fazenda Nova'),
	 ('c26065f8-414a-4606-ac04-29da4698770a','Firminópolis'),
	 ('4d462f24-8ca4-48cc-9e19-03fb9592b311','Flores de Goiás'),
	 ('34380d67-1f28-44a4-8a26-be9c730d0ddb','Formosa'),
	 ('93edd1cd-3008-411d-8700-020cf849c50a','Formoso');
INSERT INTO public.cidades (id,nome) VALUES
	 ('3fc0a366-6a01-4fd9-90c9-1ad29cfb568d','Gameleira de Goiás'),
	 ('6d9f493f-7b71-48d2-b4d3-5bed1671d588','Goianápolis'),
	 ('14239c9f-eacd-4aec-b504-32db4d80bf00','Goiandira'),
	 ('f96026a5-b207-4ce4-bbd7-67ebf5f5d812','Goianésia'),
	 ('a563d491-2166-4e5c-b5ae-1ae7406324e4','Goiânia'),
	 ('6a50311b-35a4-4a57-804d-59c7d09e690e','Goianira'),
	 ('de805086-cace-4de0-a855-5bf6f7bf099c','Goiás'),
	 ('03eeaab0-a9a0-44fa-90ea-32532509ee8b','Goiatuba'),
	 ('aa555eab-737e-445a-ab0c-554e2c7cda82','Gouvelândia'),
	 ('1e88cc62-92d7-444f-9409-60716f087513','Guapó');
INSERT INTO public.cidades (id,nome) VALUES
	 ('d1099199-cedd-4b89-b24a-348a3698efd3','Guaraíta'),
	 ('0e124a2d-d2e0-4987-a3f9-6dffeaa02dfa','Guarani de Goiás'),
	 ('aa6c82a5-b196-45f6-a6f5-d2a98e133735','Guarinos'),
	 ('0a660a5f-8665-4230-a4c6-a3317a1a849a','Heitoraí'),
	 ('e20af471-7c76-416c-be42-291058847dd9','Hidrolândia'),
	 ('2db74e2b-f764-404c-bcb4-6a5f61b35ca6','Hidrolina'),
	 ('4b07a53b-3da8-4336-b8b4-df3aea433076','Iaciara'),
	 ('a9817ade-f72c-4878-98e8-73843b0d297c','Inaciolândia'),
	 ('b91d3091-6b14-45f0-b783-cdb1f7dfe713','Indiara'),
	 ('7bd498cc-4e37-494e-9f6f-6db37f954f30','Inhumas');
INSERT INTO public.cidades (id,nome) VALUES
	 ('cba9b6ec-3ab5-46cf-b894-f806bbeb8028','Ipameri'),
	 ('497c4081-c0a2-41df-bc08-3679d2b4e866','Ipiranga de Goiás'),
	 ('aac1de4c-00c0-4b50-960f-feb51409447f','Iporá'),
	 ('3451a20b-5425-4fb1-9087-aab681575733','Israelândia'),
	 ('264e0f56-0ee1-4946-8d07-ef03e9cb8e84','Itaberaí'),
	 ('9ff07bc8-b2a4-4d2e-bf05-38e6482bafbc','Itaguari'),
	 ('4e634766-327d-46c7-b9e0-471a8c94b5d8','Itaguaru'),
	 ('2cf11fbe-f1d1-465d-b146-9e3f44dfe132','Itajá'),
	 ('b52bbdbc-8a75-4ffc-972a-d6f8a3241844','Itapaci'),
	 ('dee67f33-11ae-447a-b315-1983dc891c8d','Itapirapuã');
INSERT INTO public.cidades (id,nome) VALUES
	 ('465aa63f-f6cb-49eb-893d-9ca4007082dc','Itapuranga'),
	 ('a81ebd33-38dd-44cf-8583-6483b74be44a','Itarumã'),
	 ('93ac3fba-7fd4-4a0b-9925-091c948d5ac5','Itauçu'),
	 ('1c6e9e2a-6ac6-4ed4-a9f9-3a9308ee5277','Itumbiara'),
	 ('79f943eb-7028-4596-86ae-91d41b6b775d','Ivolândia'),
	 ('9e8386af-887c-4275-a483-65c296f73e2b','Jandaia'),
	 ('3e626bef-8f1e-4fc3-a07e-9daf7c8469ee','Jaraguá'),
	 ('136e1594-da48-463a-ba76-f103b1ad2b4a','Jataí'),
	 ('3e0264ce-1570-4c1c-83f1-a6f9eb96e155','Jaupaci'),
	 ('fec31020-c07c-4d1e-8d19-6df8509b8351','Jesúpolis');
INSERT INTO public.cidades (id,nome) VALUES
	 ('4d5941c1-a54c-4a4e-a335-f803105a6e6d','Joviânia'),
	 ('03a4b301-6cee-42f4-86ca-669517cf1fb2','Jussara'),
	 ('95c0da78-2dfe-4481-b832-b0215ce4e981','Lagoa Santa'),
	 ('e155c2e8-c5e1-4f5e-82f2-09a81d5b2b17','Leopoldo de Bulhões'),
	 ('4d1693a8-31fd-4810-b88e-420441f0eee2','Luziânia'),
	 ('244eb698-48d4-434b-b48e-f42a171d750e','Mairipotaba'),
	 ('1431ebed-863e-43ee-a80f-bbb00bba3731','Mambaí'),
	 ('06a58961-9bb5-4366-953b-647840365df5','Mara Rosa'),
	 ('e7083d2a-47c4-47e8-8af3-7485b76d5cdd','Marzagão'),
	 ('183bfbdf-430b-4cf8-97df-58748db36eb5','Matrinchã');
INSERT INTO public.cidades (id,nome) VALUES
	 ('1222f740-4525-4e4b-82e8-f1222d80b19d','Maurilândia'),
	 ('55911e96-413b-47cd-a79a-e75ecb523bc4','Mimoso de Goiás'),
	 ('178001d1-c81a-4872-87ec-f7322fa24484','Minaçu'),
	 ('0e29eeb9-584a-414a-a310-e1dc9529406b','Mineiros'),
	 ('6f428200-b3c1-4dd6-bccc-82a787756ca8','Moiçorá'),
	 ('464d6d6b-1d17-4801-b264-7e4bdf602e75','Monte Alegre de Goiás'),
	 ('422f78ad-e605-42eb-ade1-2cfd3886c762','Montes Claros de Goiás'),
	 ('6254630e-d795-4f5b-9ddf-626ca5a88f1c','Montividiu'),
	 ('8e679962-399f-4942-a8ba-ceaeaf6efa45','Montividiu do Norte'),
	 ('d5830bb6-b8e7-4af4-8f1b-489228f70764','Morrinhos');
INSERT INTO public.cidades (id,nome) VALUES
	 ('5942366a-52a8-415a-8fef-cbf273c9602a','Morro Agudo de Goiás'),
	 ('fa4bed5c-b842-4dd4-ac4f-fd7e37bc79a1','Mossâmedes'),
	 ('9d1d697f-1021-4c28-a7c9-b3dc1ff1ca42','Mozarlândia'),
	 ('c61cebdf-5c70-4ba1-aaa1-22ef0a1ddf03','Mundo Novo'),
	 ('9dcb9feb-24fb-4158-957b-5b6039cf9aef','Mutunópolis'),
	 ('dfb65c5a-6ac9-4079-926a-d8ddc8b9c7b9','Nazário'),
	 ('62830c32-ba18-4f56-b8c2-1b02a80c26a0','Nerópolis'),
	 ('632622dc-1793-43fb-871b-5eff5787e7e6','Niquelândia'),
	 ('54a2fe9d-bf60-4dfd-8b67-cc392472e853','Nova América'),
	 ('d416b7d5-b9c8-4353-b441-fa42b36dad6b','Nova Aurora');
INSERT INTO public.cidades (id,nome) VALUES
	 ('d6a3039f-0573-49b2-9e30-122ddc07f35b','Nova Crixás'),
	 ('f77e4e4b-ffe3-44a0-a7fc-4f7d607c2990','Nova Glória'),
	 ('98dc79e1-e744-4178-9013-cf72e72a8996','Nova Iguaçu de Goiás'),
	 ('ba58908a-21e0-4f50-9d4e-343f47847ac9','Nova Roma'),
	 ('768a891f-4957-4a28-87f2-6567eb95cab3','Nova Veneza'),
	 ('ffc833f9-dced-4aea-8101-ef32a61dbed5','Novo Brasil'),
	 ('7944969f-aefc-4785-a48b-a9b419f5fc58','Novo Gama'),
	 ('d11b6407-4a4b-4134-a27c-c54bd654f23d','Novo Planalto'),
	 ('8e7a4dce-d080-4b77-95e0-d22ee56560c9','Orizona'),
	 ('8b4cdaef-5424-418e-bad9-c2f36913479c','Ouro Verde de Goiás');
INSERT INTO public.cidades (id,nome) VALUES
	 ('78c6da49-a285-4901-a456-0ec467aedaee','Ouvidor'),
	 ('ced63782-00b3-44b5-b441-ef371c9ff6c1','Padre Bernardo'),
	 ('4b46e435-2f0f-4bdd-a0e7-6c82846f9a71','Palestina de Goiás'),
	 ('68d65f0a-522a-4346-8c7b-5b67eb1d39ef','Palmeiras de Goiás'),
	 ('e6121947-3489-47d8-96f1-c32d69dd0506','Palmelo'),
	 ('18caac49-1359-4431-87d8-5e85ee656e23','Palminópolis'),
	 ('70fd9466-ff14-4503-8b87-ebe7d5a87a0c','Panamá'),
	 ('bdf53f29-b697-434a-9139-e44d896becfa','Paranaiguara'),
	 ('70d4e921-166b-47c8-9c8a-8fc6a34877b2','Paraúna'),
	 ('a4037f40-cebc-4d1c-b34e-a1e30d79312f','Perolândia');
INSERT INTO public.cidades (id,nome) VALUES
	 ('39977e1b-2cf3-402a-9bd8-053935536501','Petrolina de Goiás'),
	 ('d87e1c8a-0bf6-417a-9567-dce4b39813b7','Pilar de Goiás'),
	 ('3fad131b-80ae-4c72-b838-51e719df99fe','Piracanjuba'),
	 ('d1617b07-6d69-472c-8d83-ae2bbff05052','Piranhas'),
	 ('068773de-b026-41b4-9aad-b5941e642deb','Pirenópolis'),
	 ('f5b7a5aa-bb89-425c-80e9-bd7eca2919e2','Pires do Rio'),
	 ('f28593fb-bf9f-4794-83be-b849e2b64b72','Planaltina'),
	 ('f762abaa-c584-4a34-843a-b5c39c851a30','Pontalina'),
	 ('4411cba9-7389-4455-8d7a-41273e5f6550','Porangatu'),
	 ('66b48ebc-1eea-4522-9836-755eb2198027','Porteirão');
INSERT INTO public.cidades (id,nome) VALUES
	 ('fd1a42ae-a7ec-472a-9ca0-c1f64672ac36','Portelândia'),
	 ('066c8b83-02d6-4fdd-b182-8c4e3557c568','Posse'),
	 ('2bf25192-9014-4f80-acda-4076c6498141','Professor Jamil'),
	 ('8f67ad44-389c-40b7-b8dc-47e297a63570','Quirinópolis'),
	 ('b6c10705-6283-4121-8add-39a5d9c6d4c2','Região Metropolitana de Goiânia'),
	 ('78c3c3c1-f44f-4aa6-8452-4255ca2743e4','Rialma'),
	 ('f5dad907-6391-4127-8d31-cf3ff0cd747f','Rianápolis'),
	 ('23195879-8e11-4433-8335-f32743cce296','Rio Quente'),
	 ('9740621c-ae99-468f-a532-053b89691eef','Rio Verde'),
	 ('058ffe76-b520-41d5-a855-a512592546d1','Rio Verde Região Leste');
INSERT INTO public.cidades (id,nome) VALUES
	 ('f12d3331-db11-44f6-8ce6-9141ddcfbdd1','Rio Verde Região Norte'),
	 ('0b60d9bf-6954-4aed-a485-46d8e76dcd2c','Rio Verde Região Sul'),
	 ('e7c8b376-016c-4fb5-82bc-283c7952d1b2','Rubiataba'),
	 ('c715b2a2-7e7c-4b09-b9ca-4bb7ee521bc0','Sanclerlândia'),
	 ('dbad15ce-859d-4895-9120-fa12f5447fc6','Santa Bárbara de Goiás'),
	 ('b524f9ae-c644-42b9-af3d-10f5af9f0ba0','Santa Cruz de Goiás'),
	 ('f81c0d5c-d528-41ee-9d09-c21b37eafe00','Santa Fé de Goiás'),
	 ('8ceef31c-1143-4b8d-97c8-70e1477b43e6','Santa Helena de Goiás'),
	 ('0f2a75b4-5b64-49d7-b8b5-d6755e79edc1','Santa Isabel'),
	 ('e07c438e-efc9-464e-9bd2-6c928b883954','Santa Rita do Araguaia');
INSERT INTO public.cidades (id,nome) VALUES
	 ('8f73781e-cb9f-4d3b-a01e-693a90036004','Santa Rita do Novo Destino'),
	 ('60dafccb-c86b-4601-b471-fa8754df1d7e','Santa Rosa de Goiás'),
	 ('cf5c8bb1-d6e2-4599-ae9c-297d31b8094a','Santa Tereza de Goiás'),
	 ('7a702d79-41b0-40a8-be23-80ed47e3a66a','Santa Terezinha de Goiás'),
	 ('ae544849-82e3-4238-a4fc-648d9d795a43','Santo Antônio da Barra'),
	 ('eaba7878-80d7-47f8-8fcc-055b70105e0e','Santo Antônio de Goiás'),
	 ('de4ce22b-73f1-462a-8c10-f3606a5ff840','Santo Antônio do Descoberto'),
	 ('5898b785-fd44-413a-b436-58aef9dbbe39','São Domingos'),
	 ('642df1ca-a9ba-4631-a43d-3ceea8f3eda9','São Francisco de Goiás'),
	 ('0530616d-387a-4536-991f-9af4d3101910','São João d''Aliança');
INSERT INTO public.cidades (id,nome) VALUES
	 ('617adbad-04c7-413b-b702-75f29fe6b0b5','São João da Paraúna'),
	 ('8601ae8e-1e96-41bf-8df5-a2e7be9177e4','São Luís de Montes Belos'),
	 ('e4112036-520e-4460-92ab-44b9db881541','São Luiz do Norte'),
	 ('c2158d47-ed19-4fca-b250-6f9adb1b5c8d','São Miguel do Araguaia'),
	 ('4ec4a94a-05e5-4ce3-a21d-d6bdd559854f','São Miguel do Passa Quatro'),
	 ('cec95c13-0294-477e-b00d-1dd2523616b7','São Patrício'),
	 ('ca235401-3d0a-4baa-b0a0-698b222dba35','São Simão'),
	 ('dcbd8683-30da-42ac-adf1-2140691b1564','Senador Canedo'),
	 ('b470a4be-6703-4d54-9cfd-50558ccecb75','Serranópolis'),
	 ('b591300a-7780-4773-b146-5d420f62b4f7','Silvânia');
INSERT INTO public.cidades (id,nome) VALUES
	 ('ce803429-6b17-4d94-990d-521eb2fda570','Simolândia'),
	 ('505f3bb5-cb62-495d-8b4c-7808e40c1ff5','Sítio d''Abadia'),
	 ('a9520b65-7c37-4a84-92de-cdbe4e24fed7','Taquaral de Goiás'),
	 ('e538f6e7-2cdb-4b15-8aea-ea45819adf2e','Teresina de Goiás'),
	 ('e636990f-f5d8-48fe-abac-34f6bd6927a4','Terezópolis de Goiás'),
	 ('39691cb2-e851-4850-a255-4cdc9b6da32a','Três Ranchos'),
	 ('41ce7465-0598-46d4-bd2f-d39c62efdbdd','Trindade'),
	 ('0bb8ccc5-fc0e-4100-9b99-51bd3a375dbe','Trombas'),
	 ('0a895bd7-92a7-4aad-8a97-79eb7cbe428e','Turvânia'),
	 ('107ddc98-73ab-4fc3-95bf-8a6bcb164fcc','Turvelândia');
INSERT INTO public.cidades (id,nome) VALUES
	 ('4cc913e2-5db4-4a02-aec1-396a4fc8c52d','Uirapuru'),
	 ('ea2e0b70-7dca-4310-b7d9-a536b32c944a','Uruaçu'),
	 ('c3fd51e3-ee3a-4668-ab3a-399c608cc9e3','Uruaçú'),
	 ('5b58605a-47ae-407e-af28-5a9f1f306075','Urutaí'),
	 ('6398d9ad-c45f-4f63-8540-7e40e4f0355a','Valparaíso de Goiás'),
	 ('45d0831d-e58a-4ff8-8585-128b827d4763','Várjão'),
	 ('5c37463e-15bb-4987-ac52-5fc67ddf25f6','Vianópolis'),
	 ('78e82bd6-5976-4856-9419-a7e09096887c','Vicentinópolis'),
	 ('cb3362c3-cca6-4aa9-8444-4fa9d6a2c706','Vila Boa'),
	 ('22567f42-4dfb-4a86-a528-b6e490c1c038','Vila Propício');


INSERT INTO public.eventos (personalizavel,horario,id,nome_evento) VALUES
	 (true,'2022-03-10 12:15:50','d0fbe379-8c8d-4683-843e-5ca5a9ba9c6a','Chuva'),
	 (true,'2022-03-10 12:15:50','24c35fde-25f0-4178-8e67-c9a4e69c95d1','Vento'),
	 (true,'2022-03-10 12:15:50','a665a7bf-a442-4024-9fde-7fe48b27fb5f','Temperatura Alta'),
	 (true,'2022-03-10 12:15:50','1985f34d-c878-4ec7-b9bc-94cd40d24f27','Temperatura Baixa'),
	 (true,'2022-03-10 12:15:50','dbce7e56-d8d9-4c42-911b-8bdaee7f54b4','Umidade Baixa');

-- Inserção de 50 Avisos de Teste (Corrigido com coluna diferenca)
INSERT INTO public.avisos (id, data_geracao, data_referencia, valor, unidade_medida, id_evento, id_cidade, diferenca) VALUES
-- 1. Chuva em Goiânia (Aviso Crítico)
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 50.5, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'a563d491-2166-4e5c-b5ae-1ae7406324e4', 10.5),

-- 2. Temperatura Alta em Anápolis
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 38.2, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '10f3b6f1-6072-4e4e-8661-17709b095ce5', 3.2),

-- 3. Umidade Baixa em Rio Verde
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 12.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '9740621c-ae99-468f-a532-053b89691eef', 8.0),

-- 4. Vento Forte em Caldas Novas
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 65.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '0c51fd92-adcd-4831-aee4-61f085ad161e', 15.0),

-- 5. Temperatura Baixa em Jataí
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 5.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '136e1594-da48-463a-ba76-f103b1ad2b4a', 5.0),

-- 6 a 10: Mais Chuva em cidades aleatórias
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 20.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '38732ef2-b776-483a-b04f-b4b634db446f', 0.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 15.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '55fc8533-03eb-4180-8e9f-b2c9b2849689', 0.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 80.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '39b0899b-3807-46a1-9031-d4531cbb0e66', 20.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 10.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '768f1fd6-0f59-429d-b06b-da3897d70470', 0.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 5.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'd39aa33c-8f23-4da3-8c53-b3197297efe5', 0.0),

-- 11 a 20: Temperaturas Altas
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 35.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '46f2b61f-d644-4eff-abf4-8102357eb528', 1.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 36.5, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'b26e3338-27d3-41fe-b56a-32b865eecfd9', 2.5),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 37.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'a0b8ed09-db82-40b4-8dc5-6efd086dcb53', 3.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 39.1, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '139494e5-ffad-4271-8633-998e0b2bcad3', 5.1),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 40.2, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'f5be9fd0-75ec-4c67-a04a-967b9200a7ec', 6.2),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 34.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '8ce5b84f-25ce-40d2-a7d1-65a074ddc7cb', 0.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 35.5, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '979e6488-3be9-4a21-ab3a-3f8273079d2d', 1.5),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 36.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '2737dc42-8188-4163-bbdf-bacfb0ebe95c', 2.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 38.8, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '3cfae349-2e54-405d-8571-3fc40d1e0b7f', 4.8),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 33.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'd08f0823-2956-4e46-9fde-38c82e69b64b', 0.0),

-- 21 a 30: Umidade Crítica
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 15.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '46fffbf1-4866-46a5-b556-20ed49160faa', 5.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 14.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'abe8da89-6dbb-4bc5-acf4-adfa2f62c28e', 6.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 10.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'a0460e29-76dd-4348-b006-44e875cdaf11', 10.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 18.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'b1edb2ad-bfb9-498a-8d26-4f50b4d90c6b', 2.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 19.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '0b7ebfc6-05fe-438c-8ec0-322a00ee02d8', 1.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 11.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '2c06fb5e-d797-43f7-ac67-dc3bffa8cdb0', 9.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 12.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'f6a88c00-b4ec-408d-b074-b51a5a6f1e35', 8.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 13.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'cf53e8a7-2aea-4cb8-90b8-86cbdad9e1dc', 7.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 15.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'e30ff4c4-996f-40b6-883e-67ba91f94f36', 5.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 16.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'ff95138c-270c-4562-92bf-6eae4605f26b', 4.0),

-- 31 a 40: Vento Forte
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 40.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '28b22242-f25c-4c64-bb48-519b11a147ff', 10.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 55.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'f13ba0f5-d381-41da-a383-3737d7b90884', 25.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 32.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '263967f0-ec2a-4c3a-9492-a073f889f724', 2.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 45.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'efe3494b-3ad6-4cbc-b5f1-28fc1cde7f27', 15.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 60.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '3043d02d-638e-456f-a51e-ad0791def1f5', 30.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 70.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '2e18353d-c6d2-442c-83fc-68f4fed788ff', 40.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 38.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'bf3b365a-fa28-4ab9-b29b-e8a04db565c7', 8.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 42.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '4903c394-6e24-44e8-9098-336a092b7a38', 12.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 50.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '49acaf19-58d1-4058-8158-e43d484a5bed', 20.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 35.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '498f1b14-3f2a-47ea-9f15-05dd8d252cb4', 5.0),

-- 41 a 50: Variados
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 2.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '089d7170-443a-487f-94a7-d9c863c2815a', 0.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 41.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'e5d0e4e2-9c2d-49f9-b88f-c6163d6dcf8b', 7.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 90.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '7de6d9d6-b241-4570-bdda-33f54603b582', 30.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 8.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '606d11a0-e20b-463c-aefd-4f868af8efd2', 12.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 22.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '72ca348f-9adc-4beb-9352-5c7fc049c552', 0.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 1.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '2252bfbe-ec20-4e46-9922-c0be593785df', 1.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 99.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '9a6cb886-ae7c-400e-bd1b-8c0f4a9f3525', 40.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 39.5, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '22d06dc3-6a3b-48a5-8f71-d8eb5139cc72', 5.5),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 25.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '27e5f3d0-45e8-4afb-b350-f90087733292', 0.0),
(gen_random_uuid(), CURRENT_DATE, '2025-12-04', 100.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '0279b29f-9bbd-4616-a16f-dd571671f6b9', 70.0);

-- =================================================================================
-- LOTE 1: 50 Avisos para o dia 03/12/2025 (Terça-feira)
-- Cenário: Dia muito seco e quente (Muitos alertas de Temp Alta e Umidade)
-- =================================================================================

INSERT INTO public.avisos (id, data_geracao, data_referencia, valor, unidade_medida, id_evento, id_cidade, diferenca) VALUES
-- Umidade Baixa (Crítica)
(gen_random_uuid(), '2025-12-03', '2025-12-03', 12.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'a563d491-2166-4e5c-b5ae-1ae7406324e4', 8.0), -- Goiânia
(gen_random_uuid(), '2025-12-03', '2025-12-03', 11.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '10f3b6f1-6072-4e4e-8661-17709b095ce5', 9.0), -- Anápolis
(gen_random_uuid(), '2025-12-03', '2025-12-03', 10.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '9740621c-ae99-468f-a532-053b89691eef', 10.0), -- Rio Verde
(gen_random_uuid(), '2025-12-03', '2025-12-03', 13.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '0c51fd92-adcd-4831-aee4-61f085ad161e', 7.0), -- Caldas Novas
(gen_random_uuid(), '2025-12-03', '2025-12-03', 14.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '136e1594-da48-463a-ba76-f103b1ad2b4a', 6.0), -- Jataí
(gen_random_uuid(), '2025-12-03', '2025-12-03', 15.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '38732ef2-b776-483a-b04f-b4b634db446f', 5.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 12.5, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '55fc8533-03eb-4180-8e9f-b2c9b2849689', 7.5),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 11.5, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '39b0899b-3807-46a1-9031-d4531cbb0e66', 8.5),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 9.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '768f1fd6-0f59-429d-b06b-da3897d70470', 11.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 19.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'd39aa33c-8f23-4da3-8c53-b3197297efe5', 1.0),

-- Temperatura Alta
(gen_random_uuid(), '2025-12-03', '2025-12-03', 38.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'a563d491-2166-4e5c-b5ae-1ae7406324e4', 3.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 39.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '46f2b61f-d644-4eff-abf4-8102357eb528', 4.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 37.5, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'b26e3338-27d3-41fe-b56a-32b865eecfd9', 2.5),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 40.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'a0b8ed09-db82-40b4-8dc5-6efd086dcb53', 5.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 36.8, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '139494e5-ffad-4271-8633-998e0b2bcad3', 1.8),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 35.5, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', 'f5be9fd0-75ec-4c67-a04a-967b9200a7ec', 0.5),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 38.2, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '8ce5b84f-25ce-40d2-a7d1-65a074ddc7cb', 3.2),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 39.5, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '979e6488-3be9-4a21-ab3a-3f8273079d2d', 4.5),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 37.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '2737dc42-8188-4163-bbdf-bacfb0ebe95c', 2.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 36.0, '°C', 'a665a7bf-a442-4024-9fde-7fe48b27fb5f', '3cfae349-2e54-405d-8571-3fc40d1e0b7f', 1.0),

-- Ventos (Fim de tarde)
(gen_random_uuid(), '2025-12-03', '2025-12-03', 50.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'd08f0823-2956-4e46-9fde-38c82e69b64b', 10.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 55.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '46fffbf1-4866-46a5-b556-20ed49160faa', 15.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 60.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'abe8da89-6dbb-4bc5-acf4-adfa2f62c28e', 20.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 45.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'a0460e29-76dd-4348-b006-44e875cdaf11', 5.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 48.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'b1edb2ad-bfb9-498a-8d26-4f50b4d90c6b', 8.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 52.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '0b7ebfc6-05fe-438c-8ec0-322a00ee02d8', 12.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 65.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '2c06fb5e-d797-43f7-ac67-dc3bffa8cdb0', 25.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 40.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'f6a88c00-b4ec-408d-b074-b51a5a6f1e35', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 42.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'cf53e8a7-2aea-4cb8-90b8-86cbdad9e1dc', 2.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 70.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'e30ff4c4-996f-40b6-883e-67ba91f94f36', 30.0),

-- Chuva esparsa (poucas)
(gen_random_uuid(), '2025-12-03', '2025-12-03', 5.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'ff95138c-270c-4562-92bf-6eae4605f26b', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 8.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '28b22242-f25c-4c64-bb48-519b11a147ff', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 3.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'f13ba0f5-d381-41da-a383-3737d7b90884', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 10.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '263967f0-ec2a-4c3a-9492-a073f889f724', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 12.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'efe3494b-3ad6-4cbc-b5f1-28fc1cde7f27', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 2.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '3043d02d-638e-456f-a51e-ad0791def1f5', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 1.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '2e18353d-c6d2-442c-83fc-68f4fed788ff', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 4.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'bf3b365a-fa28-4ab9-b29b-e8a04db565c7', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 6.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '4903c394-6e24-44e8-9098-336a092b7a38', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 15.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '49acaf19-58d1-4058-8158-e43d484a5bed', 0.0),

-- Temp Baixa (Madrugada)
(gen_random_uuid(), '2025-12-03', '2025-12-03', 15.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '498f1b14-3f2a-47ea-9f15-05dd8d252cb4', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 14.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '089d7170-443a-487f-94a7-d9c863c2815a', 1.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 13.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', 'e5d0e4e2-9c2d-49f9-b88f-c6163d6dcf8b', 2.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 12.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '7de6d9d6-b241-4570-bdda-33f54603b582', 3.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 11.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '606d11a0-e20b-463c-aefd-4f868af8efd2', 4.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 10.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '72ca348f-9adc-4beb-9352-5c7fc049c552', 5.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 16.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '2252bfbe-ec20-4e46-9922-c0be593785df', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 17.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '9a6cb886-ae7c-400e-bd1b-8c0f4a9f3525', 0.0),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 14.5, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '22d06dc3-6a3b-48a5-8f71-d8eb5139cc72', 0.5),
(gen_random_uuid(), '2025-12-03', '2025-12-03', 13.5, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '27e5f3d0-45e8-4afb-b350-f90087733292', 1.5);


-- =================================================================================
-- LOTE 2: 50 Avisos para o dia 01/12/2025 (Domingo)
-- Cenário: Frente Fria e Chuvosa (Muitos alertas de Chuva e Temp Baixa)
-- =================================================================================

INSERT INTO public.avisos (id, data_geracao, data_referencia, valor, unidade_medida, id_evento, id_cidade, diferenca) VALUES
-- Chuva (Generalizada)
(gen_random_uuid(), '2025-12-01', '2025-12-01', 60.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'a563d491-2166-4e5c-b5ae-1ae7406324e4', 10.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 55.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '10f3b6f1-6072-4e4e-8661-17709b095ce5', 5.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 45.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '9740621c-ae99-468f-a532-053b89691eef', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 70.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '0c51fd92-adcd-4831-aee4-61f085ad161e', 20.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 80.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '136e1594-da48-463a-ba76-f103b1ad2b4a', 30.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 90.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '38732ef2-b776-483a-b04f-b4b634db446f', 40.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 100.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '55fc8533-03eb-4180-8e9f-b2c9b2849689', 50.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 40.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '39b0899b-3807-46a1-9031-d4531cbb0e66', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 30.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '768f1fd6-0f59-429d-b06b-da3897d70470', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 25.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'd39aa33c-8f23-4da3-8c53-b3197297efe5', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 65.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '46f2b61f-d644-4eff-abf4-8102357eb528', 15.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 75.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'b26e3338-27d3-41fe-b56a-32b865eecfd9', 25.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 85.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'a0b8ed09-db82-40b4-8dc5-6efd086dcb53', 35.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 35.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '139494e5-ffad-4271-8633-998e0b2bcad3', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 95.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'f5be9fd0-75ec-4c67-a04a-967b9200a7ec', 45.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 50.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '8ce5b84f-25ce-40d2-a7d1-65a074ddc7cb', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 60.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '979e6488-3be9-4a21-ab3a-3f8273079d2d', 10.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 110.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '2737dc42-8188-4163-bbdf-bacfb0ebe95c', 60.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 30.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', '3cfae349-2e54-405d-8571-3fc40d1e0b7f', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 40.0, 'mm', 'd0fbe379-8c8d-4683-843e-5ca5a9ba9c6a', 'd08f0823-2956-4e46-9fde-38c82e69b64b', 0.0),

-- Temp Baixa
(gen_random_uuid(), '2025-12-01', '2025-12-01', 8.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', 'a563d491-2166-4e5c-b5ae-1ae7406324e4', 7.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 7.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '10f3b6f1-6072-4e4e-8661-17709b095ce5', 8.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 6.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '9740621c-ae99-468f-a532-053b89691eef', 9.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 5.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '0c51fd92-adcd-4831-aee4-61f085ad161e', 10.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 9.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '136e1594-da48-463a-ba76-f103b1ad2b4a', 6.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 10.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '46fffbf1-4866-46a5-b556-20ed49160faa', 5.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 4.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', 'abe8da89-6dbb-4bc5-acf4-adfa2f62c28e', 11.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 3.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', 'a0460e29-76dd-4348-b006-44e875cdaf11', 12.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 2.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', 'b1edb2ad-bfb9-498a-8d26-4f50b4d90c6b', 13.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 11.0, '°C', '1985f34d-c878-4ec7-b9bc-94cd40d24f27', '0b7ebfc6-05fe-438c-8ec0-322a00ee02d8', 4.0),

-- Vento
(gen_random_uuid(), '2025-12-01', '2025-12-01', 30.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '2c06fb5e-d797-43f7-ac67-dc3bffa8cdb0', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 35.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'f6a88c00-b4ec-408d-b074-b51a5a6f1e35', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 40.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'cf53e8a7-2aea-4cb8-90b8-86cbdad9e1dc', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 45.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'e30ff4c4-996f-40b6-883e-67ba91f94f36', 5.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 50.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'ff95138c-270c-4562-92bf-6eae4605f26b', 10.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 55.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '28b22242-f25c-4c64-bb48-519b11a147ff', 15.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 60.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'f13ba0f5-d381-41da-a383-3737d7b90884', 20.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 25.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '263967f0-ec2a-4c3a-9492-a073f889f724', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 28.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', 'efe3494b-3ad6-4cbc-b5f1-28fc1cde7f27', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 32.0, 'km/h', '24c35fde-25f0-4178-8e67-c9a4e69c95d1', '3043d02d-638e-456f-a51e-ad0791def1f5', 0.0),

-- Umidade
(gen_random_uuid(), '2025-12-01', '2025-12-01', 40.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '2e18353d-c6d2-442c-83fc-68f4fed788ff', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 45.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'bf3b365a-fa28-4ab9-b29b-e8a04db565c7', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 50.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '4903c394-6e24-44e8-9098-336a092b7a38', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 55.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '49acaf19-58d1-4058-8158-e43d484a5bed', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 60.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '498f1b14-3f2a-47ea-9f15-05dd8d252cb4', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 35.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '089d7170-443a-487f-94a7-d9c863c2815a', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 30.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', 'e5d0e4e2-9c2d-49f9-b88f-c6163d6dcf8b', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 25.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '7de6d9d6-b241-4570-bdda-33f54603b582', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 20.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '606d11a0-e20b-463c-aefd-4f868af8efd2', 0.0),
(gen_random_uuid(), '2025-12-01', '2025-12-01', 15.0, '%', 'dbce7e56-d8d9-4c42-911b-8bdaee7f54b4', '72ca348f-9adc-4beb-9352-5c7fc049c552', 5.0);