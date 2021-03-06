(ns codenames_clj.game
  (:require   [clojure.java.io :as io]
              [clojure.string :as string]
              [clojure.pprint :as pprint]
              [clojure.set]))
              
              

(def number-of-codenames 400)

(def codenames-list-file (io/resource "wordslist.txt"))  

(def codenames  (vec (string/split (slurp codenames-list-file) #"\n")))

(defn entry-words
  [entry]
  
  (flatten (list (key entry) (keys (val entry)))))

(defn compact
  [codenames-list full-model]
  (for [item full-model
        :when (not (not-any? true? (for [word (entry-words item)] (contains? (apply hash-set codenames-list) word))))]
    item))             

(defn incorporate-new-pair
  [word-graph [[word association] m-weight]]
  
  (if (not-any? #(clojure.string/includes? word %) (list "-" " "))
    (reduce (fn [graph new-word]
              
              (if (not-any? #(clojure.string/includes? new-word %) (list "(" " " word))
                (update-in graph
                  [word new-word]
                  (fn [counter]
                    ;(println weight)
                    (if counter
                      (+ m-weight counter)
                      m-weight))) 
                graph))
      
      word-graph
      [association])
    word-graph))

(defn reverse-hash
  [model]
  ;(doseq [x (seq (for [item model] (for [word (seq (val item))] [[(key word) (key item)] (val word)])))] 
  ;       (println x)]
  (reduce incorporate-new-pair
    {}
    (seq (for [item model
               x (for [word (seq (val item))] [[(key word) (key item)] (val word)])]
              x))))
             

                    

;(def codenames (range 400))
(defn get-codeword
  "pull from vector of words"
  [num]
  (first (drop num codenames)))

(defn gen-wordlist
  ""
  [number-of-words]
  (let [vv (range number-of-words)]
    (vec (take 25 (shuffle vv)))))
    
 
(defn get-wordlist-words
  "Simply pull words from the list of codenames at random"
  [wl]
  ;(println (vec (doall (map get-codeword wl))))
  (vec (doall (map get-codeword wl))))  


    
      


  

(defn show-gameboard
  "display the words on the board to the player"
  [words]
  ;(println (vec (string/split (slurp codenames-list-file) #"\n")))
  ;(println (partition 5 words))
  ;(println (map keyword (map str (range 5))))
  ;(println (interleave (flatten (repeat 5 (map keyword (map str (range 5))))) words))
  ;(println (apply hash-map (interleave (flatten (repeat 5 (map keyword (map str (range 5)))))  words)))
  ;(println (vec (map #(apply hash-map %) (partition 10 (interleave (flatten (repeat 5 (map keyword (map str (range 5)))))  words)))))
  ;(println (map string/join " " (partition 10 (interleave (flatten (repeat 5 (map keyword (map str (range 5))))) words))))
  (pprint/print-table (map keyword (map str (range 1 6))) (vec (doall (map #(apply hash-map %) (partition 10 (interleave (flatten (repeat 5 (map keyword (map str (range 1 6)))))  words)))))))

(def colors 
  "This definition assumes Red always plays first"
  (flatten (list (repeat 9 "red") (repeat 8 "blue") (repeat 7 "grey") "black")))

(defn assign-words
  [words]
  (apply hash-map (interleave (shuffle words) colors))) 

(defn candidates
  [game-hash compact-model]
  ;(println (take 5 (vals compact-model)))
  ;(println (seq (reduce #(clojure.set/union %1 %2) (map #(set %) (map #(keys %) (filter #(not (nil? %)) 
                                                                                  ;(map #(compact-model %) 
                                                                                    ;(map #(if (string/starts-with? % "red") %)  
                                                                                      ;(map #(game-hash %) (keys game-hash)))))
  (seq (reduce #(clojure.set/union %1 %2) (map #(set %) (map #(keys %) (filter #(not (nil? %)) 
                                                                         (map #(compact-model %) 
                                                                           (map #(if (string/starts-with? (game-hash %) "red") %)  
                                                                             (keys game-hash)))))))))
(defn group-words
  ""
  [clue color game-hash compact-model]
  (clojure.set/intersection (set (keys (compact-model clue))) (set (map #(if (string/starts-with? (game-hash %) color) %) (keys game-hash)))))

(defn show-numbers
  ""
  [clue group lit compact-model]
  [lit (interleave (seq group) (map #((compact-model clue) %) group))])
(defn get-numbers
  ""
  [clue group lit compact-model]
  {lit (map #((compact-model clue) %) group)})

(defn nonil
  "to get rid of nil in any collection"
  [coll]
  (filter #(not (nil? %)) coll))

(defn nets
  "we need numbers, let's go with max x of those on board "
  [clue game-hash compact-model]
  (let [reds (group-words clue "red" game-hash compact-model)
        blues (group-words clue "blue" game-hash compact-model)
        greys (group-words clue "grey" game-hash compact-model)
        blacks (group-words clue "black" game-hash compact-model)]
    ;(println ['reds (interleave (seq reds) (map #((compact-model clue) %) reds))])
    ;(println (show-numbers clue reds 'reds compact-model))
    ;(println clue reds)
    (reduce conj (map #(get-numbers clue % (game-hash (first %)) compact-model) [reds blues greys blacks]))))
      
    ;(println (doseq [x [reds blues greys blacks]] (show-numbers clue x 'x compact-model)))))
  ;(if (> (count (clojure.set/intersection (set (keys (compact-model clue))) (set (map #(if (string/starts-with? (game-hash %) "red") %) (keys game-hash))))) 0) clue))

(def params [1. -0.8 -1.6 -8 8. 0.001 0.6])
;params are w_red w_grey w_blue w_black c_odds_ratio c_common c_interaction
(def colorkeys ["red" "grey" "blue" "black"])

(defn odd-ratio 
  ""
  [net]
  (/ (reduce + 0 (map #(* %1 %2) (take 4 params) (map #(reduce + 0 (net %)) colorkeys))) (reduce + 0.001 (map #(reduce + 0 (net %)) colorkeys))))

(defn scoring
  ""
  [odd-rat commonality]
  (reduce + 0 
    (vec (map #(* %1 %2) (vec (take-last 3 params)) [odd-rat commonality (* commonality odd-rat)]))))

(defn rmmax
  "take larges value out of seq"
  [seq1]
  (drop-last (sort seq1)))

(defn minus-red
  "just pull the best red assoc out of the net"
  [net]
  (update net "red" rmmax))

(defn multi-clue
  "take the orig net and return a vec of nets which represent subsequent guesses"
  [net]
  (take (count (net "red")) (iterate minus-red net)))

(defn odd1
  "wrap this"
  [clue net]
  (let [odd-rat (odd-ratio net)
        commonality (reduce + 0 (net "red"))]   
    (scoring odd-rat commonality))) ;[clue (count (net "red"))]}))

(defn odds
  "put the score first, and make the (clue number) the value"
  [clue net]
  ;clue 1
  ;(println (doall (map #(reduce + 0 (net %)) colorkeys)))
  (let [nets (multi-clue net)]
    (let [pscores (remove neg? (map #(odd1 clue %) nets))]
      {(reduce + 0 pscores) [clue (count pscores)]})))

        
(defn score
  ""
  [oddrat common]
  (reduce + 0 (map #(* %1 %2) (take-last 3 params) (oddrat common (* common oddrat)))))

(defn guess2word 
  ""
  [raw]
  (reduce + (vec (map #(* %1 %2) [1 5] (map #(- % 1) (map #(Integer/parseInt %) (string/split raw #",")))))))

(defn make-clue
  [game-hash compact-model color])
  
  
(defn generate-gameboard
  "use game/codewords as default input"
  [words]
  (let [wl1 (gen-wordlist (count words))]
    (let [game-words (get-wordlist-words wl1)] ;(println web)
      ;(let [agents (assign-words game-words)]
        (show-gameboard game-words))))
        ;(show-gameboard (map #(agents %) game-words))
        ;(vec [game-words]))))
(defn what-clue 
  ""
  [cds nets pass-clue]
  ;(println pass-clue (count pass-clue))
  (if (> (count pass-clue) 0) pass-clue (let [pc (reduce conj {} (map #(odds %1 %2) cds nets))] (first (map #(pc %) (sort > (keys pc)))))))

(defn give-clue
  ""
  [pass-clue]
  
  (println pass-clue)) ;(first (map #(pass-clue %) (sort > (keys pass-clue))))))

(defn safe-read-line
  ""
  [agents words]
  (def guess (read-line))
  (while (not (contains? agents (nth words (guess2word guess))))
    (def guess (read-line)))
  guess)
(defn remaining
  ""
  [agents tagents words]
  (map #(if (contains? tagents %) % (agents %)) words))

(defn outcome 
  ""
  [agents words guess]
  (agents (nth words (guess2word guess))))

(defn execute
  "after guess is made, make appropriate actions"
  [agents guess-word]
  
  (println (agents guess-word))
  (dissoc agents guess-word))
    

