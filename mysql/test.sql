SELECT
29062025_batch_1.Kategoria,
CONCAT ('Wszystkie książki > ',REPLACE(29062025_batch_1.Kategoria,',',',Wszystkie książki >'),', Wydawnictwa > ',29062025_batch_1.Wydawca,', Autorzy > ',29062025_batch_1.Autor) as 'Categories'
FROM
29062025_batch_1
WHERE
29062025_batch_1.`EAN/UPC` IN (9788368364712)
