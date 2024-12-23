% parametrizacion

% Número de posiciones existentes
int: num_posiciones_existentes;

% Coordenadas de las ciudades (matriz de tamaño [num_posiciones_existentes, 2])
array[1..num_posiciones_existentes, 1..2] of int: ciudades;

% Tamaño de la matriz
int: tamano_matriz;

% Matriz de segmento de población
array[1..tamano_matriz, 1..tamano_matriz] of int: matriz_segmento_poblacion;

% Matriz de entorno empresarial
array[1..tamano_matriz, 1..tamano_matriz] of int: matriz_entorno_empresarial;

% Número de programas
int: num_programas;


%--------------------------------------------------------------------------------------------------------------------


% Variables

%ubicacion
array[1..tamano_matriz, 1..tamano_matriz] of var 0..1: ubicaciones;



% Inicialización de las ubicaciones predefinidas con intercambio de coordenadas
array[1..tamano_matriz, 1..tamano_matriz] of int: ubicaciones_predefinidas = 
  array2d(1..tamano_matriz, 1..tamano_matriz, 
    [if exists(c in 1..num_posiciones_existentes) 
        (i = ciudades[c, 2] /\ j = ciudades[c, 1]) 
     then 1 else 0 endif | i, j in 1..tamano_matriz]);


% Restricción: las ubicaciones predefinidas deben permanecer como 1
constraint forall(i, j in 1..tamano_matriz)(
  ubicaciones_predefinidas[i, j] = 1 -> ubicaciones[i, j] = 1
);



% Restricción: solo se pueden construir n ubicaciones
constraint sum(i in 1..tamano_matriz, j in 1..tamano_matriz)(ubicaciones[i,j]) = num_programas + num_posiciones_existentes;


% Restricción: no se puede construir en zonas adyacentes
constraint forall(i, j in 1..tamano_matriz)(
  ubicaciones[i, j] = 1 ->
  forall(k in max(1, i-1)..min(tamano_matriz, i+1), 
         l in max(1, j-1)..min(tamano_matriz, j+1))(
    % Evitar modificar la propia posición (i, j)
    (k != i \/ l != j) -> ubicaciones[k, l] = 0
  )
);



% Definir una función para calcular la suma de una celda y sus vecinas
function int: suma_vecinos(array[1..tamano_matriz, 1..tamano_matriz] of int: matriz, int: i, int: j) =
  sum(k in max(1, i-1)..min(tamano_matriz, i+1), 
      l in max(1, j-1)..min(tamano_matriz, j+1))(
        matriz[k, l]
  );

% Restricción: Segmento poblacional >= 25 y Entorno empresarial >= 20
constraint forall(i, j in 1..tamano_matriz)(
  ubicaciones[i, j] = 1 ->
  (suma_vecinos(matriz_segmento_poblacion, i, j) >= 25 /\
   suma_vecinos(matriz_entorno_empresarial, i, j) >= 20)
);

% Actualización de la ganancia total
var int: ganancia = sum(i, j in 1..tamano_matriz where ubicaciones[i, j] = 1)(
  suma_vecinos(matriz_segmento_poblacion, i, j) +
  suma_vecinos(matriz_entorno_empresarial, i, j)
);

% Ganancia calculada únicamente para las coordenadas de las ciudades
var int: ganancia_ciudades = sum(c in 1..num_posiciones_existentes)(
  suma_vecinos(matriz_segmento_poblacion, ciudades[c, 2], ciudades[c, 1]) +
  suma_vecinos(matriz_entorno_empresarial, ciudades[c, 2], ciudades[c, 1])
);

solve maximize ganancia;


%----------------------------------------------------------------------------------------------------------------------------------------



% Mostrar las ubicaciones de las universidades y la ganancia 
%output [ "ubicaciones:\n", 
%show([ubicaciones[i,j] | i in 1..tamano_matriz, j in 1..tamano_matriz]), "\nganancia: ", show(ganancia), "\n" ];



% Mostrar las ubicaciones y las ganancias calculadas
output [
"ubicaciones:\n", 
 show([ubicaciones[i,j] | i in 1..tamano_matriz, j in 1..tamano_matriz]), 
 "\nganancia: ", show(ganancia), 
 "\nganancia_ciudades: ", show(ganancia_ciudades), "\n"
];














