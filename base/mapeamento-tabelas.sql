
--drop view vw_info_aluno
create view vw_info_aluno as
	with recursive tmp_professor as
	(
		select iddiario, 
		max(id_prof_1) as id_prof_1, max(id_prof_2) as id_prof_2, max(id_prof_3) as id_prof_3, max(id_prof_4) as id_prof_4,
		max(nome_prof_1) as nome_prof_1, max(nome_prof_2) as nome_prof_2, max(nome_prof_3) as nome_prof_3, max(nome_prof_4) as nome_prof_4
		from 
		(
			select iddiario, 
			case when ordem = 1 then idprofessor else null end as id_prof_1,
			case when ordem = 2 then idprofessor else null end as id_prof_2,
			case when ordem = 3 then idprofessor else null end as id_prof_3,
			case when ordem = 4 then idprofessor else null end as id_prof_4,
			case when ordem = 1 then nomeprofessor else null end as nome_prof_1,
			case when ordem = 2 then nomeprofessor else null end as nome_prof_2,
			case when ordem = 3 then nomeprofessor else null end as nome_prof_3,
			case when ordem = 4 then nomeprofessor else null end as nome_prof_4
			from 
				(
					select i.iddiario, row_number() over (partition by i.iddiario order by i.iddiario) as ordem, i.idprofessor, j.nomeprofessor 
					from tbdiario.tbdiarioaula i 
						left join tbprofessor.tbprofessor j on i.idprofessor = cast(j.idprofessor as varchar)
					where j.nomeprofessor is not null
					group by i.iddiario, i.idprofessor, j.nomeprofessor 
					order by 1
				) a
		) b
		group by iddiario
	),

	tmp_aluno_metaconceito as
	(
		select k.idmeta, k.iddisciplina, k.idfasenota, k.idtipometa, l.idaluno, l.idturma, l.idmetaconceito, m.descricao, m.idperiodo, m.idserie
		from tbmeta.tbmeta k 
			left join tbmeta.tbmetafasenotaaluno l on k.idmeta = l.idmeta
			left join tbmeta.tbmetaconceito m on l.idmetaconceito = m.idmetaconceito
	)

	 select a.idaluno, a.iddisciplina, f.nomedisciplina, a.idturma, m.nometurma, a.idfasenota,
	b.idperiodo, c.siglaperiodo, b.numerofase, b.nomefase, b.idserie, d.codigoserie, d.nomeserie, e.nomecurso,
	 a.notafase, a.faltas, a.quantaulasdadas
	,g.descricao
	, h.nome_prof_1, h.nome_prof_2, h.nome_prof_3, h.nome_prof_4, j.descricao as situacao_aluno
	, k.descricao as avaliacao_desc, k.idperiodo as ava_idperiodo, k.idserie as ava_idserie
	,l.nomealuno, l.datanascimento, l.sexo
	from tbfase.tbfasenotaaluno a 
		left join tbfase.tbfasenota b on a.idfasenota = b.idfasenota
		left join outrastabelas.tbperiodo c on b.idperiodo = c.idperiodo
		left join tbserie.tbserie d on b.idserie = d.idserie
		left join outrastabelas.tbcursofases e on d.idcurso = e.idcurso
		left join outrastabelas.tbdisciplina f on a.iddisciplina = f.iddisciplina
		left join tbdiario.tbdiario g on a.iddisciplina = g.iddisciplina and a.idturma = g.idturma and a.idfasenota = g.idfasenota
		left join tmp_professor h on h.iddiario = g.iddiario
		left join tbsituacaoalunodisciplina.tbsituacaoalunodisciplina i 
			on i.iddisciplina = a.iddisciplina and i.idturma = a.idturma and i.idaluno = a.idaluno and i.idfasenotaatual = a.idfasenota
		left join tbsituacaoalunodisciplina.tbtiposituacaoalunodisciplina j on i.situacaoatual= j.tiposituacaoalunodisciplina
		left join tmp_aluno_metaconceito k on  k.iddisciplina = a.iddisciplina and k.idaluno = a.idaluno and k.idturma = a.idturma --and k.idfasenota = a.idfasenota and
		left join tbaluno.tbaluno l on a.idaluno = l.idaluno
		left join tbturma.tbturma m on m.idturma = a.idturma
	order by a.idaluno, c.siglaperiodo, d.idserie, a.iddisciplina, b.numerofase