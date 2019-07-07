(ns codenames-clj.core
  (:require [clojure.java.io :as io]
            [clojure.string :as string])
  (:gen-class))

(def number-of-codenames 400)

(def codenames-list-file (io/resource "wordslist.txt"))

(def codenames-get  (vec (string/split (slurp codenames-list-file) #"\n")))
(def codenames (range 400))
(defn get-codeword
  "pull from vector of words"
  [num]
  (take 1 (drop num codenames-get))
  )

(defn gen-wordlist
  ""
  []
  (let [vv (repeat 25 number-of-codenames)]
    (vec (map rand-int vv))
    )

  )

(defn get-wordlist-words
  "Simply pull words from the list of codenames at random"
  [wl]

    (vec (map get-codeword wl))


  )

(defn generate-gameboard
  ""
  [words]

  )

(defn five-sub
  "counting from 1 "
  [words row]
  (subvec words (* 5 (- row 1)) (* 5 row))
  )

(defn show-gameboard
  "display the words on the board to the player"
  [words]
  (doseq [row (range 1 6)]
    (println (five-sub words row))
  )
)


(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (println "Hello, World!")

  ;(println codenames-get)
  ;(println (vec (repeat 25 number-of-codenames)))
  (let [wl1 (gen-wordlist)]
    (println wl1)
    (println (- 9 1))
    (println (get-wordlist-words wl1))
    ;(println (subvec (get-wordlist-words wl1) 0 5))
    (show-gameboard (get-wordlist-words wl1))
  )
  )
