UPDATE 29062025_batch_1
SET 29062025_batch_1.Kategoria = replace(29062025_batch_1.Kategoria, '.', ',')
WHERE
29062025_batch_1.`EAN/UPC` IN (9788368364712)